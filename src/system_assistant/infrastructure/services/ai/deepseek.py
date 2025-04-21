from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent
from loguru import logger
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_system_message_param import \
    ChatCompletionSystemMessageParam
from openai.types.chat.chat_completion_user_message_param import \
    ChatCompletionUserMessageParam
from pydantic import SecretStr

from system_assistant.application.services.ai.base import LLM
from system_assistant.application.services.ai.prompts import \
    construct_system_assistant_prompt

from .openai_agent import BaseReactOpenAIAgent

DEEPSEEK_CHAT_MODEL = 'deepseek-chat'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'


class DeepSeek(LLM):
    def __init__(self, api_key: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    async def make_request(self, text: str) -> str:
        logger.info(f'Request to DeepSeek: input_messages_length={len(text)}')
        response = await self.client.chat.completions.create(
            messages=[
                ChatCompletionSystemMessageParam(
                    role='system', content=construct_system_assistant_prompt(),
                ),
                ChatCompletionUserMessageParam(role='user', content=text),
            ],
            model=DEEPSEEK_CHAT_MODEL,
            stream=False,
        )
        logger.info(f'Response from Deepseek: response_id={response.id}')
        return response.choices[0].message.content  # type: ignore


class DeepSeekOpenAIAgent(BaseReactOpenAIAgent):
    def initialize(self) -> ChatOpenAI | CompiledGraph:
        _llm = ChatOpenAI(
            model=DEEPSEEK_CHAT_MODEL,
            base_url=DEEPSEEK_BASE_URL,
            api_key=SecretStr(self._config.deepseek_api_key),
            temperature=self.temperature
        )
        if self.tools:
            _llm = _llm.bind_tools(self.tools)  # type: ignore
            agent_executor = create_react_agent(
                _llm, tools=self.tools, checkpointer=self._memory_saver,
            )
            return agent_executor
        return _llm
