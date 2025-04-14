from loguru import logger
from openai import AsyncOpenAI
from openai.types.chat.chat_completion_system_message_param import \
    ChatCompletionSystemMessageParam
from openai.types.chat.chat_completion_user_message_param import \
    ChatCompletionUserMessageParam

from system_assistant.application.services.ai.base import LLM


GEMINI_MODEL = 'gemini-2.0-flash'
GEMINI_API_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/openai/'
PROMPT = """
You are voice assistant who helps people and makes them happy, because they are speeking with you,
most of the time give short and right answers.

IMPORTANT:
    1. Do not format responses and do not add emojis or similar characters
    2. You cannot write any code
    3. You cannot show any visual examples
"""


class Gemini(LLM):
    def __init__(self, api_key: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key, base_url=GEMINI_API_BASE_URL)

    async def make_request(self, text: str) -> str:
        logger.info(f'Request to Gemini: input_messages_length={len(text)}')
        response = await self.client.chat.completions.create(
            messages=[
                ChatCompletionSystemMessageParam(role='system', content=PROMPT),
                ChatCompletionUserMessageParam(role='user', content=text),
            ],
            model=GEMINI_API_BASE_URL,
            stream=False,
        )
        logger.info(f'Response from Gemini: response_id={response.id}')
        return response.choices[0].message.content  # type: ignore
