import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from  config import settings
from  db.database import Base


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(settings.get_test_db_url())
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def setup_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture(scope="function")
async def session(async_session_factory, setup_database):
    async with async_session_factory() as session:
        try:
            yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()
