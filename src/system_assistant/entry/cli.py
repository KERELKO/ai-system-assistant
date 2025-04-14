import asyncio
import sys

import speech_recognition as sr  # type: ignore[import-untyped]
from loguru import logger

from system_assistant.application.commands.generate_ai_voice_response import \
    GenerateAIVoiceResponseCommand
from system_assistant.application.mediator import Mediator
from system_assistant.core.container import init_container
from system_assistant.infrastructure.services.sound.base import SoundService


async def main():
    container = init_container()

    mediator: Mediator = container.resolve(Mediator)  # type: ignore
    sound_service: SoundService = container.resolve(SoundService)  # type: ignore

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
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Exit')
        sys.exit(0)
