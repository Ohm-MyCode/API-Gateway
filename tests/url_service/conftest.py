import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from url_service.main import app
from url_service.models import Url
from url_service.url_routes import get_db

db_url= "postgresql+psycopg://test:test@localhost:5433/urltestdb"
engine = create_async_engine(db_url,pool_size=5,max_overflow=5,pool_timeout=20)
TestSession = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)


async def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        await db.close()


@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    async with TestSession() as session:
        await session.execute(delete(Url))
        await session.commit()
    yield

app.dependency_overrides[get_db]=override_get_db

@pytest.fixture(autouse=True)
def client():
    with TestClient(app) as client:
        yield client

# class FakeRedis:
#     async def get(self, key):
#         return None

#     async def set(self, key, value, ex=None):
#         pass

# app.state.redis_client = FakeRedis()