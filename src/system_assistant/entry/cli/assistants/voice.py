from dataclasses import dataclass

import speech_recognition as sr  # type: ignore[import-untyped]
from loguru import logger

from system_assistant.application.commands.request_system_help import RequestSystemHelpCommand
from system_assistant.application.services.text_to_speech.base import BaseTextToSpeechService
from system_assistant.core.types import AIAnswer
from system_assistant.infrastructure.services.sound.base import SoundService

from .base import Assistant


@dataclass(eq=False, repr=False, slots=True)
class VoiceAssistant(Assistant):
    text_to_speech_service: BaseTextToSpeechService
    sound_service: SoundService

    async def run(self):
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

                ai_answer: AIAnswer = (await self.mediator.handle_command(
                    RequestSystemHelpCommand(
                        message=text,
                        system_context=self.context.system_context,
                        chat_id=self.context.chat_id,
                    )
                ))[0]
                speech = await self.text_to_speech_service.synthesize(
                    text=ai_answer['content'].strip(), output='bytes'
                )
                self.sound_service.play_sound(speech)  # type: ignore
                text = ''
