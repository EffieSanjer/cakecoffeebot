import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from backend.config import settings
from backend.database import Base


@pytest_asyncio.fixture(scope="function")
async def engine():
    engine = create_async_engine(settings.get_test_db_url())
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def setup_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope='function')
async def session(engine, setup_database):
    async with AsyncSession(engine) as session:
        yield session
