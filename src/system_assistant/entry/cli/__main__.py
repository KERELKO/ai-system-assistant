import asyncio
import sys
import typing as t
import uuid
from pathlib import Path
import click
from loguru import logger
from punq import (  # type: ignore
    Container,
)

from system_assistant.application.mediator import Mediator
from system_assistant.application.services.text_to_speech.base import BaseTextToSpeechService
from system_assistant.core import ROOT
from system_assistant.core.config import Config
from system_assistant.core.types import (
    LLMConfiguration,
    SystemContext,
)
from system_assistant.infrastructure.db.sqlite.init import (
    init_db,
)
from system_assistant.infrastructure.ioc import (
    init_base_container,
    register_gateway,
    register_llm,
    register_mediator,
    register_mediator_handlers,
    register_services,
)
from system_assistant.infrastructure.services.ai.tools.docker import DOCKER_TOOLS
from system_assistant.infrastructure.services.ai.tools.os import OS_TOOLS
from system_assistant.infrastructure.services.ai.tools.search import build_brave_search_tool
from system_assistant.infrastructure.services.sound.base import SoundService

from .assistants.base import Context, BaseSystemAssistant
from .assistants.voice import SystemAssistant


@click.command()
@click.option(
    '--llm', default='deepseek', help='LLM, available: deepseek|gemini', show_default=True,
)
@click.option('--temperature', default=1.0, help='LLM temperature', show_default=True)
@click.option(
    '--enable-tools',
    default=False,
    help='Give LLM ability to use system tools',
    show_default=True,
    is_flag=True,
)
@click.option(
    '--cwd',
    default=str(ROOT),
    help='Current working directory. Use to provide rich llm context',
)
@click.option(
    '--debug',
    default=False,
    help='Option to enable debug mode. In this mode logging level is set to DEBUG',
    is_flag=True,
)
@click.option(
    '--storage',
    default='memory',
    help='Storage. Available: memory|sqlite|dgraph',
    show_default=True,
)
@click.option(
    '--chat-id',
    default=None,
    help=(
        'Use to provide custom chat ID. If persistent storage is available — saves chat history '
        'there and later this chat history can be loaded to provide LLM with rich context'
    ),
)
@click.option(
    '--input',
    default='text',
    help=(
        'Input type. Avaiable: text|voice\n'
        'If "voice" selected microphone will be used as source for input'
    ),
    show_default=True,
)
@click.option(
    '--output',
    default='text',
    help=(
        'Output type. Available: text|voice\nIf "voice" selected assistant will use '
        'voice to answer'
    ),
    show_default=True,
)
def system_assistant(
    temperature: float,
    llm: str,
    enable_tools: bool,
    cwd: str,
    debug: bool,
    chat_id: str | None,
    storage: str,
    input: str,
    output: str,
):
    chat_id = chat_id or str(uuid.uuid4())

    loop = asyncio.get_event_loop()

    if debug:
        logger.configure(handlers=[{"sink": sys.stdout, "level": "DEBUG"}])
    else:
        logger.configure(handlers=[{"sink": sys.stdout, "level": "INFO"}])

    if input not in ('text', 'voice'):
        raise ValueError(f'Invalid input option: {input}')

    if output not in ('text', 'voice'):
        raise ValueError(f'Invalid output option: {output}')

    logger.debug(f'LLM temperature={temperature}')
    logger.debug(f'LLM={llm}')
    logger.debug(f'enable-tools={enable_tools}')
    logger.debug(f'cwd={cwd}')
    logger.debug(f'chat-id={chat_id}')

    llm_configuration = LLMConfiguration(
        llm_temperature=temperature, llm=llm, llm_enable_tools=enable_tools,
    )
    context = Context(
        llm_conf=llm_configuration,
        debug=debug,
        chat_id=chat_id,
        system_context=SystemContext.default(cwd=Path(cwd))
    )

    container = build_cli_container(storage, llm_configuration)
    config = t.cast(Config, container.resolve(Config))

    if storage == 'sqlite':
        loop.run_until_complete(init_db(config))

    mediator = t.cast(Mediator, container.resolve(Mediator))
    sound_service = t.cast(SoundService, container.resolve(SoundService))
    text_to_speech_service = t.cast(
        BaseTextToSpeechService, container.resolve(BaseTextToSpeechService),
    )

    assistant: BaseSystemAssistant = SystemAssistant(
        mediator,
        context,
        recognizer_type='whisper',
        text_to_speech_service=text_to_speech_service,
        sound_service=sound_service,
        input=input,  # type: ignore
        output=output,  # type: ignore
    )
    loop.run_until_complete(assistant.run())


def build_cli_container(
    storage: str,
    llm_cf: LLMConfiguration,
) -> Container:
    container = init_base_container()

    config = t.cast(Config, container.resolve(Config))

    brave_search_tool = build_brave_search_tool(config)

    tools = [*OS_TOOLS, *DOCKER_TOOLS, brave_search_tool] if llm_cf.llm_enable_tools else []

    register_llm(
        container,
        llm_tools=tools,
        llm_type=llm_cf.llm,
        llm_temperature=llm_cf.llm_temperature,
    )
    register_gateway(container, storage)
    register_services(container)
    register_mediator_handlers(container)
    register_mediator(container)

    return container


if __name__ == '__main__':
    try:
        asyncio.run(system_assistant())
    except KeyboardInterrupt:
        logger.info('Exit')
        sys.exit(0)
