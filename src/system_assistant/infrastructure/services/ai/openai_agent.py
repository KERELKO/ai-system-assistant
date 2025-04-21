from abc import abstractmethod

from langchain.tools import BaseTool
from langchain_core.messages import BaseMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_openai.chat_models import ChatOpenAI
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.graph import CompiledGraph

from system_assistant.core.config import Config
from system_assistant.domain.entities.chat import Chat
from system_assistant.core.types import AIAnswer
from system_assistant.infrastructure.services.ai.utils import \
    to_langchain_message


class BaseReactOpenAIAgent:
    def __init__(
        self,
        config: Config,
        tools: list[BaseTool],
        memory_saver: BaseCheckpointSaver = MemorySaver(),
        temperature: float = 1.0,
    ):
        self._memory_saver = memory_saver
        self._config = config
        self.tools = tools
        self.temperature = temperature

        self._agent = self.initialize()

    @abstractmethod
    def initialize(self) -> ChatOpenAI | CompiledGraph:
        raise NotImplementedError

    async def chat(self, chat: Chat) -> AIAnswer:
        converted_messsages = [to_langchain_message(msg) for msg in chat.messages]
        ai_answer = AIAnswer(is_successful=True, chat_id=chat.id, content='')
        async for messages in self._agent.astream(
            input={'messages': converted_messsages},  # type: ignore
            config=RunnableConfig(configurable={'thread_id': chat.id}),
            stream_mode='values',
        ):
            last_message: BaseMessage = messages['messages'][-1]  # type: ignore
            if last_message.type in ['ai', 'system', 'assistant']:
                ai_answer['content'] = last_message.content  # type: ignore
        return ai_answer

    def update_settings(self, temperature: float | None = None, tools: list | None = None):
        if tools is not None:
            self.tools = tools
        if temperature is not None:
            self.temperature = temperature
        self._agent = self.initialize()
