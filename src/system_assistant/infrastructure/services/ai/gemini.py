from langchain_openai.chat_models import ChatOpenAI
from langgraph.graph.graph import CompiledGraph
from loguru import logger
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_system_message_param import \
    ChatCompletionSystemMessageParam
from openai.types.chat.chat_completion_user_message_param import \
    ChatCompletionUserMessageParam
from langgraph.prebuilt import create_react_agent
from pydantic import SecretStr

from system_assistant.application.services.ai.base import LLM
from system_assistant.application.services.ai.prompts import construct_system_assistant_prompt
from .openai_agent import BaseReactOpenAIAgent


GEMINI_MODEL = 'gemini-2.0-flash'
GEMINI_API_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/openai/'


class Gemini(LLM):
    def __init__(self, api_key: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key, base_url=GEMINI_API_BASE_URL)

    async def make_request(self, text: str) -> str:
        logger.info(f'Request to Gemini: input_messages_length={len(text)}')
        response = await self.client.chat.completions.create(
            messages=[
                ChatCompletionSystemMessageParam(
                    role='system', content=construct_system_assistant_prompt()
                ),
                ChatCompletionUserMessageParam(role='user', content=text),
            ],
            model=GEMINI_API_BASE_URL,
            stream=False,
        )
        logger.info(f'Response from Gemini: response_id={response.id}')
        return response.choices[0].message.content  # type: ignore


class GeminiOpenAIAgent(BaseReactOpenAIAgent):
    def build_agent(self) -> CompiledGraph:
        _llm = ChatOpenAI(
            model=GEMINI_MODEL,
            base_url=GEMINI_API_BASE_URL,
            api_key=SecretStr(self._config.gemini_api_key),
            temperature=self.temperature,
        )
        _llm = _llm.bind_tools(self.tools)  # type: ignore

        agent_executor = create_react_agent(
            model=_llm, tools=self.tools, checkpointer=self._memory_saver,
        )
        return agent_executor
