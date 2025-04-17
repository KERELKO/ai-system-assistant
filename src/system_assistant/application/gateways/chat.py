import typing as t

from system_assistant.core.exceptions import ApplicationException
from system_assistant.domain.entities.chat import Chat
from system_assistant.domain.vo import ID, Message


class ChatGateway(t.Protocol):
    async def get_by_id(self, id: ID) -> Chat | None:
        raise NotImplementedError

    async def save(self, chat: Chat) -> ID:
        ...

    async def append_message(self, chat_id: ID, message: Message):
        ...


class FakeChatGateway:
    def __init__(self):
        self.chats = {}

    async def get_by_id(self, id: ID) -> Chat | None:
        chat = self.chats.get(id, None)
        if not chat:
            raise ApplicationException('Not Found')
        return chat

    async def save(self, chat: Chat) -> ID:
        self.chats[chat.id] = chat
        return chat.id

    async def append_message(self, chat_id: ID, message: Message):
        self.chats[chat_id].append_message(message)
