from dataclasses import dataclass

from loguru import logger

from system_assistant.application.services.ai.base import LLM
from system_assistant.application.services.text_to_speech.base import \
    BaseTextToSpeechService
from system_assistant.core.types import Output, Speech

from .base import BaseCommandHandler, Command


@dataclass(eq=False, slots=True, repr=False)
class GenerateAIVoiceResponseCommand(Command):
    text: str
    output: Output


class GenerateAIVoiceResponseCommandHandler(
    BaseCommandHandler[GenerateAIVoiceResponseCommand, Speech],
):
    def __init__(
        self,
        text_to_speech_service: BaseTextToSpeechService,
        llm: LLM,
    ):
        self._llm = llm
        self._text_to_speech_service = text_to_speech_service

    async def handle(self, command: GenerateAIVoiceResponseCommand) -> Speech:
        logger.info(f'{self.__class__.__name__} handling {command.__class__.__name__}')

        ai_response = await self._llm.make_request(command.text)

        speech = await self._text_to_speech_service.synthesize(ai_response, command.output)

        return speech
