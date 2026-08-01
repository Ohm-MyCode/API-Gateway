import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .models import Base
from .config import dbsettings

if dbsettings.AUTH_DB is None:
    raise ValueError("Check Url service DB")

engine = create_async_engine(dbsettings.AUTH_DB,pool_size=5,max_overflow=5,pool_timeout=20)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())

SessionLocal = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)
