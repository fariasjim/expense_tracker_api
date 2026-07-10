import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlmodel import SQLModel
import redis.asyncio

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:////workspace/shop.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# SQLModel uses standard SQLAlchemy engines under the hood
engine = create_async_engine(
    DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
)


# Enforce SQLite foreign key rules on connect hooks
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Session factory for producing async execution scopes
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
redis_client = redis.asyncio.from_url(REDIS_URL, decode_responses=True)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
