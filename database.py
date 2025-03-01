from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models import Model

async_engine = create_async_engine(
    "sqlite+aiosqlite:///todos.db"
)

new_session = async_sessionmaker(async_engine, expire_on_commit=False, autoflush=False)

async def enable_foreign_keys():
    async with async_engine.connect() as conn:
        await conn.execute(text("PRAGMA foreign_keys = ON"))



async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)



async def delete_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)