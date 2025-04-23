from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine
from loguru import logger

from system_assistant.domain.entities.chat import Chat
from system_assistant.domain.vo import ID, Message


class SQLiteChatGateway:
    def __init__(self, engine: AsyncEngine):
        self.session_factory = async_sessionmaker(engine, expire_on_commit=True, autoflush=False)

    async def get_by_id(self, id: ID) -> Chat | None:
        async with self.session_factory() as session:
            chat = await session.get(Chat, id)
        logger.info(f'Found {1 if chat else 0} chat by id: id={id}')
        return chat

    async def save(self, chat: Chat) -> ID:
        chat_id = chat.id
        async with self.session_factory() as session:
            session.add(chat)
            await session.commit()
        logger.info(f'Saved chat: id={chat_id}')
        return chat_id

    async def append_message(self, chat_id: ID, message: Message):
        raise NotImplementedError
