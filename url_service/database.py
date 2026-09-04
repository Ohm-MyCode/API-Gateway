import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from url_service.config import settings
from url_service.metrics import register_db_metrics
from url_service.models import Base

if settings.URL_DB is None:
    raise ValueError("Check Url service DB")

engine = create_async_engine(settings.URL_DB,pool_size=5,max_overflow=5,pool_timeout=20)
register_db_metrics(engine)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())

SessionLocal = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)
