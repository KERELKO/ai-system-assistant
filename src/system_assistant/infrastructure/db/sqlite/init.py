from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from system_assistant.core.config import Config

from .tables import mapper_registry


async def init_db(config: Config):
    engine = get_engine(config)

    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)


def get_engine(config: Config) -> AsyncEngine:
    engine = create_async_engine(url=config.sqlite_url, echo=True)
    return engine
