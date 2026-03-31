# tests/conftest.py

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from pymongo import AsyncMongoClient

from app.main import app
from app.database.connection import database
from app.config.database import MONGODB_URI, TEST_DATABASE_NAME, MONGO_OPTIONS


@pytest_asyncio.fixture(scope="session", autouse=True)
async def use_test_database():
    """
    Runs once for the entire test session.

    - Before tests: redirect the shared `database` object to the test
      database instead of the development database.
    - After tests:  drop the test database entirely and close the connection.
    """
    database.client = AsyncMongoClient(MONGODB_URI, **MONGO_OPTIONS)
    await database.client.aconnect()
    database.db = database.client[TEST_DATABASE_NAME]
    print(f"\n[conftest] Using test database: {TEST_DATABASE_NAME}")

    yield  # all tests run here

    await database.client.drop_database(TEST_DATABASE_NAME)
    await database.client.close()
    print(f"\n[conftest] Dropped test database: {TEST_DATABASE_NAME}")


@pytest_asyncio.fixture(autouse=True)
async def clear_todos():
    """
    Runs before each individual test.
    Empties the todos collection so every test starts with a clean slate.
    """
    await database.db["todos"].delete_many({})


@pytest_asyncio.fixture
async def client():
    """
    Provides an async HTTP client wired directly to the FastAPI app.
    No real network port is opened — requests go through memory only.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac