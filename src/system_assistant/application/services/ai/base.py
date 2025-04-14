from abc import ABC, abstractmethod


class LLM(ABC):
    @abstractmethod
    async def make_request(self, text: str) -> str:
        ...


class FakeLLM(LLM):
    async def make_request(self, text: str) -> str:
        return "I'm LLM"
