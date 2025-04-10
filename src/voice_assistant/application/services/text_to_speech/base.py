from abc import ABC, abstractmethod

from voice_assistant.core.types import Output, Speech


class BaseTextToSpeechService(ABC):
    @abstractmethod
    async def convert(self, text: str, output: Output) -> Speech:
        ...
