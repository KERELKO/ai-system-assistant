from abc import ABC, abstractmethod


class AIAgent(ABC):
    @abstractmethod
    async def make_request(self, text: str) -> str:
        ...
