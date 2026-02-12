import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.models import Base
from app.main import app
from app.core.session import get_db


# Тестовая БД
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создаем тестовый engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Переопределение зависимости get_db"""
    async with TestingSessionLocal() as session:
        yield session

# Применяем переопределение
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def setup_database():
    """Создание и удаление таблиц для каждого теста"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

@pytest.fixture
async def db_session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    """Сессия БД для тестов"""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Клиент для тестирования"""

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def product_list() -> list[dict]:
    return [
        {
            "name": "product1",
            "price": 111,
        },
        {
            "name": "product2",
            "price": 222,
        },
        {
            "name": "product3",
            "price": 333,
        },
    ]
