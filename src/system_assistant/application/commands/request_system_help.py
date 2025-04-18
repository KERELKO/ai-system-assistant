from dataclasses import dataclass
import uuid

from loguru import logger

from system_assistant.application.gateways.chat import ChatGateway
from system_assistant.application.services.ai.base import AIAgent
from system_assistant.core.types import SystemContext
from system_assistant.domain.entities.chat import Chat
from system_assistant.domain.vo import ID, AIAnswer, Message
from system_assistant.application.services.ai.prompts import construct_system_assistant_prompt

from .base import BaseCommandHandler, Command


@dataclass(eq=False, slots=True, repr=False)
class RequestSystemHelpCommand(Command):
    message: str
    system_context: SystemContext
    chat_id: ID | None = None


class RequestSystemHelpCommandHandler(BaseCommandHandler[RequestSystemHelpCommand, AIAnswer]):
    def __init__(
        self,
        chat_gateway: ChatGateway,
        ai_agent: AIAgent
    ) -> None:
        self._chat_gateway = chat_gateway
        self._ai_agent = ai_agent

    def _create_chat(self, command: RequestSystemHelpCommand) -> Chat:
        title = command.message if len(command.message) < 200 else f'{command.message}...'
        content = construct_system_assistant_prompt(
            operating_system=command.system_context.operating_system,
            distribution=command.system_context.distribution,
            current_dir=command.system_context.cwd,
            directory_list=command.system_context.directory_list,
        )
        chat = Chat(
            id=command.chat_id or str(uuid.uuid4()),
            title=title,
            messages=[Message(sender='assistant', content=content)],
        )
        return chat

    async def handle(self, command: RequestSystemHelpCommand) -> AIAnswer:
        logger.info('Handling system help command')
        message = Message(sender='user', content=command.message)

        if command.chat_id is not None:
            chat = await self._chat_gateway.get_by_id(command.chat_id)
            if chat is None:
                chat = self._create_chat(command)
        else:
            chat = self._create_chat(command)

        chat.add_message(message)
        ai_answer = await self._ai_agent.chat(chat)
        chat.add_message(Message(sender='assistant', content=ai_answer['content']))  # type: ignore
        await self._chat_gateway.save(chat)
        logger.info(f'Saved chat: chat_id={command.chat_id}')
        return ai_answer
