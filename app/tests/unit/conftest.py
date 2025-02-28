import asyncio
from typing import TYPE_CHECKING, AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import NullPool, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from tests.database import SyncTestSession, TestSession, set_task
from config import DATABASE_URL



@pytest.fixture(scope="session")
def event_loop() -> Generator["asyncio.AbstractEventLoop", None, None]:
    loop = asyncio.get_event_loop_policy().get_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def connection() -> AsyncGenerator["AsyncConnection", None]:
    set_task(asyncio.current_task())
    database_url = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
    engine = create_async_engine(database_url, poolclass=NullPool)
    conn = await engine.connect()
    TestSession.configure(bind=conn)
    # migrate_db("head")

    yield conn

    # migrate_db("base")
    await conn.close()
    await engine.dispose()

@pytest_asyncio.fixture(autouse=True)
async def db(connection: "AsyncConnection") -> AsyncGenerator["AsyncSession", None]:
    await connection.begin_nested()
    session = TestSession()

    yield session

    await session.close()
    await TestSession.remove()
    await connection.rollback()