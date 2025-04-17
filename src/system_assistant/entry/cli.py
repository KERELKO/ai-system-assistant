import asyncio
import sys
import typing as t
from pathlib import Path
from punq import Container  # type: ignore[import-untyped]

import click
import speech_recognition as sr  # type: ignore[import-untyped]
from loguru import logger

from system_assistant.application.commands.generate_ai_voice_response import \
    GenerateAIVoiceResponseCommand
from system_assistant.application.commands.request_system_help_command import \
    RequestSystemHelpCommand
from system_assistant.application.mediator import Mediator
from system_assistant.application.services.ai.base import AIAgent
from system_assistant.core import ROOT
from system_assistant.infrastructure.ioc import init_container
from system_assistant.core.types import SystemContext
from system_assistant.infrastructure.services.sound.base import SoundService


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
def setup(
    temperature: float,
    llm: str,
    enable_tools: bool,
    cwd: str,
    debug: bool
):
    print(temperature)
    print(llm)
    print(enable_tools)
    print(cwd)

    container = init_container(llm)
    ai_agent = t.cast(AIAgent, container.resolve(AIAgent))

    if enable_tools is False:
        ai_agent.update_settings(temperature=temperature, tools=[])
    else:
        ai_agent.update_settings(temperature=temperature)

    container.register(AIAgent, instance=ai_agent)

    asyncio.run(system_assistant(container, debug, cwd))


async def system_assistant(
    container: Container,
    debug: bool,
    cwd: str,
    **kwargs,
):

    mediator = t.cast(Mediator, container.resolve(Mediator))
    sound_service = t.cast(SoundService, container.resolve(SoundService))
    system_context = SystemContext.default(cwd=Path(cwd))

    if debug:
        while True:
            user_input = input('Enter message ("q" to exit): ')
            if user_input.lower() == 'q':
                break
            ai_response = (await mediator.handle_command(
                RequestSystemHelpCommand(system_context=system_context, message=user_input)
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
                audio = r.listen(source, timeout=3)
            except sr.WaitTimeoutError:
                logger.warning("Didn't recorgnize user voice or user didn't speak")
                continue

            try:
                text = r.recognize_google(audio)  # type: ignore
                logger.info(f'Recorgnized user voice: {text}')
            except sr.UnknownValueError:
                logger.error("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                logger.error(
                    f"Could not request results from Google Speech Recognition service; {e}"
                )

            logger.debug(text)
            text = text.lower().strip()

            if text == 'exit':
                logger.info('Closing program')
                sys.exit(0)

            ai_response = (await mediator.handle_command(
                GenerateAIVoiceResponseCommand(text=text, output='bytes')
            ))[0]
            sound_service.play_sound(ai_response)
            text = ''


if __name__ == '__main__':
    try:
        setup()
    except KeyboardInterrupt:
        logger.info('Exit')
        sys.exit(0)
