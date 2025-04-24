from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine
from loguru import logger

from system_assistant.domain.entities.chat import Chat
from system_assistant.domain.vo import ID


class SQLiteChatGateway:
    def __init__(self, engine: AsyncEngine):
        self.session_factory = async_sessionmaker(engine, expire_on_commit=True, autoflush=False)

    async def get_by_id(self, id: ID) -> Chat | None:
        logger.info(f'Get chat by id: id={id}')
        async with self.session_factory() as session:
            chat = await session.get(Chat, id)
        return chat

    async def save(self, chat: Chat) -> ID:
        logger.info(f'Save chat: id={chat.id}')
        chat_id = chat.id
        async with self.session_factory() as session:
            session.add(chat)
            await session.commit()
        return chat_id
