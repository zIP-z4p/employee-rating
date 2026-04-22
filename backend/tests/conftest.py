import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import NullPool

from app.main import app
from app.api.deps import get_db, get_cache
from app.infrastructure.database.base import Base
from app.infrastructure.database.models import (  # noqa — регистрация моделей
    employee, rating, department
)

TEST_DATABASE_URL = (
    "postgresql+asyncpg://test_user:test_pass@localhost:5433/test_rating_db"
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Тестовый HTTP клиент с подменой зависимостей"""
    
    class MockCache:
        async def get_snapshot(self, *args): return None
        async def set_snapshot(self, *args): pass
        async def invalidate_period(self, *args): return 0
    
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_cache] = lambda: MockCache()
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


# Фикстуры для тестовых данных
@pytest_asyncio.fixture
async def sample_department(db_session: AsyncSession):
    from app.infrastructure.database.models.department import Department
    dept = Department(name="Engineering", code="ENG")
    db_session.add(dept)
    await db_session.flush()
    return dept


@pytest_asyncio.fixture
async def sample_employee(db_session: AsyncSession, sample_department):
    from app.infrastructure.database.models.employee import Employee
    from datetime import date
    emp = Employee(
        department_id=sample_department.id,
        full_name="John Doe",
        email="john.doe@company.com",
        position="Senior Engineer",
        hire_date=date(2020, 1, 15),
    )
    db_session.add(emp)
    await db_session.flush()
    return emp


@pytest_asyncio.fixture
async def sample_metric(db_session: AsyncSession):
    from app.infrastructure.database.models.rating import (
        RatingMetric, RatingCategory
    )
    from decimal import Decimal
    metric = RatingMetric(
        name="Code Quality",
        category=RatingCategory.QUALITY,
        weight=Decimal("0.300"),
    )
    db_session.add(metric)
    await db_session.flush()
    return metric

