import os
from typing import AsyncIterator, Final
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)

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


async def get_db() -> AsyncIterator[AsyncSession]:
    """
    Generates a database session that auto closes not depending on the function calling it.

    Returns:
        AsyncSession: Database session
    """
    async with _session_maker() as session:
        yield session
