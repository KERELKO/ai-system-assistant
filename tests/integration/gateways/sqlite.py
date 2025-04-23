import uuid

import pytest
from loguru import logger

from system_assistant.core.config import Config
from system_assistant.domain.entities.chat import Chat
from system_assistant.domain.vo import Message
from system_assistant.infrastructure.db.sqlite.init import get_engine
from system_assistant.infrastructure.gateways.chat.sqlite import SQLiteChatGateway


@pytest.mark.asyncio
async def main():
    config = Config()

    engine = get_engine(config)

    gate = SQLiteChatGateway(engine)

    chat = Chat(
        id=str(uuid.uuid4()),
        title='first chat',
        messages=[Message(sender='user', content='hello!')]
    )

    chat_id = await gate.save(chat)
    logger.info(chat_id)

    chat = await gate.get_by_id(chat_id)
    logger.info(chat)
