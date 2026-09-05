from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    URL_DB:str
    redis_host:str
    redis_port:int
    ttl:int=3600
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()