import asyncio
import sys
import typing as t
import uuid
from dataclasses import dataclass
from pathlib import Path

import click
import speech_recognition as sr  # type: ignore[import-untyped]
from loguru import logger
from punq import (  # type: ignore
    Container,
    Scope,
)

from system_assistant.application.commands.request_system_help import RequestSystemHelpCommand
from system_assistant.application.gateways.chat import ChatGateway
from system_assistant.application.mediator import Mediator
from system_assistant.application.services.text_to_speech.base import BaseTextToSpeechService
from system_assistant.core import ROOT
from system_assistant.core.config import Config
from system_assistant.core.types import (
    AIAnswer,
    SystemContext,
)
from system_assistant.infrastructure.db.sqlite.init import (
    get_engine,
    init_db,
)
from system_assistant.infrastructure.gateways.chat.sqlite import SQLiteChatGateway
from system_assistant.infrastructure.ioc import (
    init_base_container,
    register_llm,
    register_mediator,
    register_mediator_handlers,
    register_services,
)
from system_assistant.infrastructure.services.ai.tools.docker import DOCKER_TOOLS
from system_assistant.infrastructure.services.ai.tools.os import OS_TOOLS
from system_assistant.infrastructure.services.sound.base import SoundService


@dataclass(eq=False, slots=True)
class LLMConfiguration:
    llm_temperature: float
    llm: str
    llm_enable_tools: bool


@dataclass(eq=False, slots=True)
class Context:
    system_context: SystemContext
    llm_conf: LLMConfiguration
    debug: bool
    chat_id: str | None


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
    help=(
        'Option to enable debug mode. '
        'In this mode speaking does not work and logging level set to DEBUG'
    ),
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
def setup_system_assistant(
    temperature: float,
    llm: str,
    enable_tools: bool,
    cwd: str,
    debug: bool,
    chat_id: str | None,
    storage: str,
):
    chat_id = chat_id or str(uuid.uuid4())

    loop = asyncio.get_event_loop()

    if debug:
        logger.configure(handlers=[{"sink": sys.stdout, "level": "DEBUG"}])
    else:
        logger.configure(handlers=[{"sink": sys.stdout, "level": "INFO"}])

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

    loop.run_until_complete(
        system_assistant(mediator, sound_service, text_to_speech_service, context),
    )


def build_cli_container(
    storage: str,
    llm_cf: LLMConfiguration,
) -> Container:
    container = init_base_container()
    config = t.cast(Config, container.resolve(Config))

    tools = [*OS_TOOLS, *DOCKER_TOOLS] if llm_cf.llm_enable_tools else []

    if llm_cf.llm not in ('deepseek', 'gemini', 'fake'):
        raise NotImplementedError(f'Unsupported LLM: {llm_cf.llm}')

    register_llm(
        container,
        llm_tools=tools,
        llm_type=llm_cf.llm,  # type: ignore
        llm_temperature=llm_cf.llm_temperature,
    )

    if storage == 'memory':  # In base container already
        ...
    elif storage == 'sqlite':
        engine = get_engine(config)
        container.register(ChatGateway, instance=SQLiteChatGateway(engine), scope=Scope.singleton)
    else:
        raise NotImplementedError(f'Unsupported storage: {storage}')

    register_services(container)
    register_mediator_handlers(container)
    register_mediator(container)

    return container


async def system_assistant(
    mediator: Mediator,
    sound_service: SoundService,
    text_to_speech_service: BaseTextToSpeechService,
    context: Context,
):
    if context.debug:
        while True:
            user_input = input('Enter message ("q" to exit): ')
            if user_input.lower() == 'q':
                break
            ai_response = (await mediator.handle_command(
                RequestSystemHelpCommand(
                    system_context=context.system_context,
                    message=user_input,
                    chat_id=context.chat_id,
                )
            ))[0]
            logger.info(ai_response)
        return

    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        text = ''

        while True:
            logger.info('Listening...')
            try:
                audio = r.listen(source)
            except sr.WaitTimeoutError:
                logger.warning("Didn't recorgnize user voice or user didn't speak")
                continue

            try:
                text = r.recognize_google(audio)  # type: ignore
                logger.debug(f'Recorgnized user voice: {text}')
            except sr.UnknownValueError:
                logger.error("Google Speech Recognition could not understand audio")
                continue
            except sr.RequestError as e:
                logger.error(
                    f"Could not request results from Google Speech Recognition service; {e}"
                )
                continue

            text = text.strip()

            if not text:
                continue
            if text.lower() == 'exit':
                logger.info('Exit')
                return

            ai_answer: AIAnswer = (await mediator.handle_command(
                RequestSystemHelpCommand(
                    message=text, system_context=context.system_context, chat_id=context.chat_id)
            ))[0]
            speech = await text_to_speech_service.synthesize(
                text=ai_answer['content'].strip(), output='bytes'
            )
            sound_service.play_sound(speech)  # type: ignore
            text = ''


if __name__ == '__main__':
    try:
        asyncio.run(setup_system_assistant())
    except KeyboardInterrupt:
        logger.info('Exit')
        sys.exit(0)
