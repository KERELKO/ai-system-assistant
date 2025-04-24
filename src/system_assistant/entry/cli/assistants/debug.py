from pprint import pprint

from loguru import logger

from system_assistant.application.commands.request_system_help import RequestSystemHelpCommand
from system_assistant.core.types import AIAnswer

from .base import Assistant


class DebugAssistant(Assistant):
    async def run(self):
        while True:
            user_input = input('Enter message ("q" to exit): ')
            if user_input.lower() == 'q':
                break
            ai_response: AIAnswer = (await self.mediator.handle_command(
                RequestSystemHelpCommand(
                    system_context=self.context.system_context,
                    message=user_input,
                    chat_id=self.context.chat_id,
                )
            ))[0]
            pprint(ai_response)
            logger.info(f'AI answer content: {ai_response['content']}')
