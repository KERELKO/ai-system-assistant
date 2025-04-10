from openai import AsyncOpenAI
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam
from openai.types.chat.chat_completion_system_message_param import ChatCompletionSystemMessageParam

from voice_assistant.core import logger

from voice_assistant.application.services.ai.base import AIAgent


DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
PROMPT = """
You are voice assistant who helps people and makes them happy, because they are speeking with you
"""


class DeepSeek(AIAgent):
    def __init__(self, api_key: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    async def make_request(self, text: str) -> str:
        logger.info(f'Request to DeepSeek: input_messages_length={len(text)}')
        response = await self.client.chat.completions.create(
            messages=[
                ChatCompletionSystemMessageParam(role='system', content=PROMPT),
                ChatCompletionUserMessageParam(role='user', content=text),
            ],
            model='deepseek-chat',
            stream=False,
        )
        logger.info(f'Response from Deepseek: response_id={response.id}')
        return response.choices[0].message.content  # type: ignore
