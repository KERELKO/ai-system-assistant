from sqlalchemy import Table, Column, String, Text, ForeignKey, Integer
from sqlalchemy.orm import registry, relationship

from system_assistant.domain.entities.chat import Chat, Message


mapper_registry = registry()


message_table = Table(
    'message',
    mapper_registry.metadata,
    Column('id', Integer, primary_key=True),
    Column('chat_id', String, ForeignKey('chat.id'), nullable=False),
    Column('sender', String(10), nullable=False),
    Column('content', Text, nullable=False),
)


chat_table = Table(
    'chat',
    mapper_registry.metadata,
    Column('id', String, primary_key=True, unique=True),
    Column('title', String(100), nullable=False),
)

mapper_registry.map_imperatively(
    Chat,
    chat_table,
    properties={
        'messages': relationship(
            'Message',
            backref='chat',
            collection_class=list,
            cascade='all, delete-orphan',
            lazy='joined',
        )
    }
)

mapper_registry.map_imperatively(Message, message_table)
