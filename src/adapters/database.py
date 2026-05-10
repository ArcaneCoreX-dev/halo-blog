"""Database engine and session management.

Copyright (c) 2026 ArcaneCoreX-dev - MIT License
See LICENSE file for details.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.domain.models import Base

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """Dependency: yield a DB session."""
    async with async_session() as session:
        yield session
