from abc import ABC, abstractmethod

from system_assistant.core.types import Output, Speech


class BaseTextToSpeechService(ABC):
    @abstractmethod
    async def synthesize(self, text: str, output: Output) -> Speech:
        ...
