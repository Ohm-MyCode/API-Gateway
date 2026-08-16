import asyncio
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .models import Base


class Settings(BaseSettings):
    URL_DB:str
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()

if settings.URL_DB is None:
    raise ValueError("Check Url service DB")

engine = create_async_engine(settings.URL_DB,pool_size=5,max_overflow=5,pool_timeout=20)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())

SessionLocal = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)
