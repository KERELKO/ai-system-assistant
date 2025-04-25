from dataclasses import dataclass
from typing import Literal

import speech_recognition as sr  # type: ignore[import-untyped]
from loguru import logger

from system_assistant.application.commands.request_system_help import RequestSystemHelpCommand
from system_assistant.application.services.text_to_speech.base import BaseTextToSpeechService
from system_assistant.core.types import AIAnswer
from system_assistant.infrastructure.services.sound.base import SoundService

from .base import BaseSystemAssistant


@dataclass(eq=False, repr=False, slots=True)
class SystemAssistant(BaseSystemAssistant):
    text_to_speech_service: BaseTextToSpeechService
    sound_service: SoundService
    recognizer_type: Literal['google', 'whisper'] = 'whisper'
    input: Literal['text', 'voice'] = 'voice'
    output: Literal['text', 'voice'] = 'voice'

    def _recognize(self, recognizer: sr.Recognizer, audio) -> str:
        if self.recognizer_type == 'google':
            return recognizer.recognize_goolge(audio)  # type: ignore
        elif self.recognizer_type == 'whisper':
            return recognizer.recognize_whisper(audio)  # type: ignore
        raise ValueError(f'Invalid recognizer type: {self.recognizer_type}')

    def _get_text_input(self) -> str | Literal['exit']:
        user_input = input('Enter message ("q" to exit): ')
        if user_input == 'q':
            return 'exit'
        return user_input

    def _get_audio_input(
        self, recognizer: sr.Recognizer, source: sr.Microphone,
    ) -> str | Literal['exit']:
        logger.info('Listening...')
        try:
            audio = recognizer.listen(source)
        except sr.WaitTimeoutError:
            logger.warning("Didn't recorgnize user voice or user didn't speak")
            return ''
        try:
            text = self._recognize(recognizer, audio)
            logger.debug(f'Recorgnized user voice: {text}')
        except sr.UnknownValueError:
            logger.error("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            logger.error(
                f"Could not request results from Google Speech Recognition service; {e}"
            )
        return ''

    def _answer_text(self, text: str):
        print(text)

    async def _answer_voice(self, text: str):
        speech = await self.text_to_speech_service.synthesize(
            text=text.strip(), output='bytes'
        )
        self.sound_service.play_sound(speech)  # type: ignore

    async def run(self):
        if self.input == 'text':
            await self._run_with_text_input()
        elif self.input == 'voice':
            await self._run_with_voice_input()

    async def _run_with_text_input(self):
        answer = self._answer_text if self.output == 'text' else self._answer_voice
        while True:
            text = self._get_text_input().strip()
            if not text:
                continue
            if text == 'exit':
                logger.info('Exit')
                return

            ai_answer: AIAnswer = (await self.mediator.handle_command(
                RequestSystemHelpCommand(
                    message=text,
                    system_context=self.context.system_context,
                    chat_id=self.context.chat_id,
                )
            ))[0]
            logger.debug(ai_answer)
            answer(ai_answer['content'])
            text = ''

    async def _run_with_voice_input(self):
        answer = self._answer_text if self.output == 'text' else self._answer_voice

        r = sr.Recognizer()

        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            text = ''

            while True:
                text = self._get_audio_input(r, source).strip()

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
                logger.debug(ai_answer)
                answer(ai_answer['content'])
                text = ''
