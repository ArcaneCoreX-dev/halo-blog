"""Pytest configuration and fixtures.

Copyright (c) 2026 ArcaneCoreX-dev - MIT License
See LICENSE file for details.
"""

import asyncio
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.adapters.database import get_db
from src.domain.models import Base
from src.main import app

# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def admin_token(client: AsyncClient) -> str:
    """Create admin user and return JWT token."""
    from src.services.auth import hash_password
    from src.domain.models import User

    async with TestSessionLocal() as session:
        admin = User(
            username="testadmin",
            password_hash=hash_password("testpass"),
            display_name="Test Admin",
            role="admin",
        )
        session.add(admin)
        await session.commit()

    response = await client.post(
        "/admin/api/login",
        json={"username": "testadmin", "password": "testpass"},
    )
    return response.json()["access_token"]
