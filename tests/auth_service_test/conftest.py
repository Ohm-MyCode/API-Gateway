import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from auth_service.auth_routes import get_db
from auth_service.main import app
from auth_service.models import RefreshToken, User

db_url= "postgresql+psycopg://test:test@localhost:5433/testdb"
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
        await session.execute(delete(RefreshToken))
        await session.execute(delete(User))
        await session.commit()
    yield

app.dependency_overrides[get_db]=override_get_db

client = TestClient(app)