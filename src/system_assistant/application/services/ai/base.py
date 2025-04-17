from abc import ABC, abstractmethod
from typing import Callable, Protocol

from system_assistant.domain.entities.chat import Chat
from system_assistant.domain.vo import AIAnswer


class LLM(ABC):
    @abstractmethod
    async def make_request(self, text: str) -> str:
        ...


class FakeLLM(LLM):
    async def make_request(self, text: str) -> str:
        return "I'm LLM"


class AIAgent(Protocol):
    """LLM extended with tools"""
    temperature: float
    tools: list[Callable]

    @abstractmethod
    async def chat(self, chat: Chat) -> AIAnswer:
        ...

    @abstractmethod
    def remove_tools(self):
        ...


class FakeAIAgent:
    def __init__(self):
        self.temperature = 1.0
        self.tools = []

    async def chat(self, chat: Chat) -> AIAnswer:
        return AIAnswer(chat_id=chat.id, is_successful=True, content="I'm fake AI agent")

    def remove_tools(self):
        ...
