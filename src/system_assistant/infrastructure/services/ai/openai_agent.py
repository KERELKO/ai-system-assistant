from typing import Literal

from langchain.tools import BaseTool
from langchain_core.messages import BaseMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_openai.chat_models import ChatOpenAI
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent
from pydantic import SecretStr

from system_assistant.core.config import Config
from system_assistant.domain.entities.chat import Chat
from system_assistant.domain.vo import AIAnswer
from system_assistant.infrastructure.services.ai.utils import \
    to_langchain_message


class ReactOpenAIAgent:
    def __init__(
        self,
        config: Config,
        memory_saver: BaseCheckpointSaver,
        tools: list[BaseTool],
        temperature: float = 1.0,
    ):
        self._memory_saver = memory_saver
        self.__config = config
        self.tools = tools
        self.temperature = temperature

        self._llm: ChatOpenAI
        self.__llm_type: Literal['deepseek', 'gemini']
        self.agent_executor: CompiledGraph

    def init_deepseek_react_agent(self):
        from system_assistant.infrastructure.services.ai.deepseek import (
            DEEPSEEK_BASE_URL, DEEPSEEK_CHAT_MODEL)

        _llm = ChatOpenAI(
            model=DEEPSEEK_CHAT_MODEL,
            base_url=DEEPSEEK_BASE_URL,
            api_key=SecretStr(self.__config.deepseek_api_key),
            temperature=self.temperature
        )
        self.__llm_type = 'deepseek'
        if self.tools:
            self._llm = _llm.bind_tools(self.tools)  # type: ignore
            self.agent_executor = create_react_agent(
                self._llm, tools=self.tools, checkpointer=self._memory_saver,
            )

    def init_gemini_react_agent(self):
        from system_assistant.infrastructure.services.ai.gemini import (
            GEMINI_API_BASE_URL, GEMINI_MODEL)

        _llm = ChatOpenAI(
            model=GEMINI_MODEL,
            base_url=GEMINI_API_BASE_URL,
            api_key=SecretStr(self.__config.gemini_api_key),
            temperature=self.temperature,
        )
        self.__llm_type = 'gemini'
        self._llm = _llm.bind_tools(self.tools)  # type: ignore

        self.agent_executor = create_react_agent(
            self._llm, tools=self.tools, checkpointer=self._memory_saver,
        )

    async def chat(self, chat: Chat) -> AIAnswer:
        converted_messsages = [to_langchain_message(msg) for msg in chat.messages]
        ai_answer = AIAnswer(is_successful=True, chat_id=chat.id, content='')
        async for messages in self.agent_executor.astream(
            input={'messages': converted_messsages},
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

        if self.__llm_type == 'deepseek':
            self.init_deepseek_react_agent()
        elif self.__llm_type == 'gemini':
            self.init_gemini_react_agent()
