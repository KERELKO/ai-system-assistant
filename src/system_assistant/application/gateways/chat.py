import typing as t

from loguru import logger

from system_assistant.domain.entities.chat import Chat
from system_assistant.domain.vo import ID


class ChatGateway(t.Protocol):
    async def get_by_id(self, id: ID) -> Chat | None:
        raise NotImplementedError

    async def save(self, chat: Chat) -> ID:
        ...


class InMemoryChatGateway:
    def __init__(self):
        self.chats = {}

    async def get_by_id(self, id: ID) -> Chat | None:
        chat = self.chats.get(id, None)
        return chat

    async def save(self, chat: Chat) -> ID:
        self.chats[chat.id] = chat
        logger.debug(self.chats)
        return chat.id
