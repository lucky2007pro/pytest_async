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

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@contextlib.asynccontextmanager
async def override_lifespan(app: FastAPI):
    yield

app.router.lifespan_context = override_lifespan


@pytest_asyncio.fixture(autouse=True)
async def create_tables():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
