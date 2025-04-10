import asyncio
import sys

import speech_recognition as sr  # type: ignore[import-untyped]
from loguru import logger

from voice_assistant.application.commands.generate_ai_voice_response import \
    GenerateAIVoiceResponseCommand
from voice_assistant.application.mediator import Mediator
from voice_assistant.core.container import init_container


async def main():
    logger.info('Start listening...')
    container = init_container()

    mediator = container.resolve(Mediator)

    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        text = ''

        while True:
            try:
                audio = r.listen(source, timeout=2)
            except sr.WaitTimeoutError:
                logger.warning("Didn't recorgnize user voice or user didn't speak")
                logger.info('Sleep for 5 seconds')
                await asyncio.sleep(5)
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

            text = text.lower()

            if text == 'exit':
                logger.info('Closing program')
                sys.exit(0)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Exit')
        sys.exit(0)
