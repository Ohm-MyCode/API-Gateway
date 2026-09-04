import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from auth_service.config import dbsettings
from auth_service.metrics import register_db_metrics
from auth_service.models import Base

if dbsettings.AUTH_DB is None:
    raise ValueError("Check Url service DB")

engine = create_async_engine(dbsettings.AUTH_DB,pool_size=5,max_overflow=5,pool_timeout=20)
register_db_metrics(engine)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())

SessionLocal = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)
