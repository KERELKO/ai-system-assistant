import asyncio
import sys
import typing as t
import uuid
from dataclasses import dataclass
from pathlib import Path

import click
import speech_recognition as sr  # type: ignore[import-untyped]
from loguru import logger

from system_assistant.application.commands.request_system_help import \
    RequestSystemHelpCommand
from system_assistant.application.mediator import Mediator
from system_assistant.application.services.ai.base import AIAgent
from system_assistant.application.services.text_to_speech.base import \
    BaseTextToSpeechService
from system_assistant.core import ROOT
from system_assistant.core.types import SystemContext, AIAnswer
from system_assistant.infrastructure.ioc import init_container
from system_assistant.infrastructure.services.sound.base import SoundService


@dataclass(eq=False, slots=True)
class Context:
    temperature: float
    llm: str
    enable_tools: bool
    system_context: SystemContext
    debug: bool
    chat_id: str | None


@click.command()
@click.option('--temperature', default=1.0, help='LLM temperature', show_default=True)
@click.option(
    '--llm', default='deepseek', help='LLM, available: deepseek|gemini', show_default=True,
)
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
    help='Option to enable debug mode, in this mode speaking does not work',
    is_flag=True,
)
@click.option(
    '--chat-id',
    default=None,
    help='Use to set custom chat ID, can be used later to provide richer context to LLM',
)
def setup(
    temperature: float,
    llm: str,
    enable_tools: bool,
    cwd: str,
    debug: bool,
    chat_id: str | None,
):
    chat_id = chat_id or str(uuid.uuid4())

    if debug:
        logger.configure(handlers=[{"sink": sys.stdout, "level": "DEBUG"}])
    else:
        logger.configure(handlers=[{"sink": sys.stdout, "level": "INFO"}])

    logger.debug(f'LLM temperature={temperature}')
    logger.debug(f'LLM={llm}')
    logger.debug(f'enable-tools={enable_tools}')
    logger.debug(f'cwd={cwd}')
    logger.debug(f'chat-id={chat_id}')

    container = init_container(llm)
    ai_agent = t.cast(AIAgent, container.resolve(AIAgent))

    if enable_tools is False:
        ai_agent.update_settings(temperature=temperature, tools=[])
    else:
        ai_agent.update_settings(temperature=temperature)

    container.register(AIAgent, instance=ai_agent)

    context = Context(
        temperature=temperature,
        llm=llm,
        enable_tools=enable_tools,
        debug=debug,
        chat_id=chat_id,
        system_context=SystemContext.default(cwd=Path(cwd))
    )
    mediator = t.cast(Mediator, container.resolve(Mediator))
    sound_service = t.cast(SoundService, container.resolve(SoundService))
    text_to_speech_service = t.cast(
        BaseTextToSpeechService, container.resolve(BaseTextToSpeechService)
    )

    asyncio.run(
        system_assistant(
            mediator,
            sound_service,
            text_to_speech_service,
            context,
        )
    )


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

            logger.debug(text)
            text = text.lower().strip()

            if not text:
                continue
            elif text == 'exit':
                logger.info('Closing program')
                sys.exit(0)

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
        setup()
    except KeyboardInterrupt:
        logger.info('Exit')
        sys.exit(0)
