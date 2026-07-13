import pytest
import pytest_asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
import contextlib

from main import app
from db import Base, get_db

# Create in-memory sqlite for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Override lifespan to avoid hitting the real postgres DB during tests
@contextlib.asynccontextmanager
async def override_lifespan(app: FastAPI):
    yield

app.router.lifespan_context = override_lifespan


@pytest_asyncio.fixture(autouse=True)
async def create_tables():
    """Create and drop tables before and after each test."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    """Fixture to provide an async test client."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db_session():
    """Fixture to provide a database session for tests if needed."""
    async with TestingSessionLocal() as session:
        yield session
