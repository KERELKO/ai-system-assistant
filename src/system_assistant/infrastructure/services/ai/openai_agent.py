import typing as t

from langchain.tools import BaseTool
from langchain_openai.chat_models import ChatOpenAI
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph.graph import CompiledGraph
from pydantic import SecretStr

from system_assistant.core.config import Config


class OpenAIAgent:
    def __init__(
        self,
        config: Config,
        memory_saver: BaseCheckpointSaver,
        tools: list[BaseTool],
        llm: t.Literal['gemini', 'deepseek'] = 'deepseek'
    ):
        self._memory_saver = memory_saver
        self.__config = config
        self._tools = tools

        if llm == 'deepseek':
            self.__init_deepseek_react_agent()
        elif llm == 'gemini':
            self.__init_gemini_react_agent()

        self._llm: ChatOpenAI
        self.agent_executor: CompiledGraph

    def __init_deepseek_react_agent(self):
        from system_assistant.infrastructure.services.ai.deepseek import (
            DEEPSEEK_CHAT_MODEL, DEEPSEEK_BASE_URL)

        self._llm = ChatOpenAI(
            model=DEEPSEEK_CHAT_MODEL,
            base_url=DEEPSEEK_BASE_URL,
            api_key=SecretStr(self.__config.deepseek_api_key),
        )

        self.agent_executor = create_react_agent(
            self._llm, tools=self._tools, checkpointer=self._memory_saver,
        )

    def __init_gemini_react_agent(self):
        from system_assistant.infrastructure.services.ai.gemini import (
            GEMINI_API_BASE_URL, GEMINI_MODEL)

        self._llm = ChatOpenAI(
            model=GEMINI_MODEL,
            base_url=GEMINI_API_BASE_URL,
            api_key=SecretStr(self.__config.gemini_api_key),
        )

        self.agent_executor = create_react_agent(
            self._llm, tools=self._tools, checkpointer=self._memory_saver,
        )
