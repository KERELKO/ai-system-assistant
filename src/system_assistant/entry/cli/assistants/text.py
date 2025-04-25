from pprint import pprint

from system_assistant.application.commands.request_system_help import RequestSystemHelpCommand
from system_assistant.core.types import AIAnswer

from .base import BaseSystemAssistant


class TextSystemAssistant(BaseSystemAssistant):
    """Simple system assistant that takes user's input from `input()` function"""

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
            print(ai_response['content'])
