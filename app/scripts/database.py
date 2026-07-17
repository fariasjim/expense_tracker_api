import os
from typing import AsyncIterator, Final
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from app.models.schemas import User, Expenses
from sqlmodel import SQLModel

# Encapsulating the DATABASE_URL variable private[unchangeable].
DATABASE_URL: Final[str] = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://test_user:secretkey@db:5432/test_db"
)

# Encapsulating engine for write protection.
_engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)

# Encapsulated _session_maker which returns a AsyncSession
_session_maker = async_sessionmaker(
    bind=_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """
    Initiate the Database with all the tables instantly when the application starts.
    Fixes database empty exception.
    """
    async with _engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db() -> AsyncIterator[AsyncSession]:
    """
    Generates a database session that auto closes not depending on the function calling it.

    Returns:
        AsyncSession: Database session
    """
    async with _session_maker() as session:
        yield session
