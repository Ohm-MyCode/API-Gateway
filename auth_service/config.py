from pydantic_settings import BaseSettings, SettingsConfigDict

class DBSettings(BaseSettings):
    AUTH_DB:str
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

class Settings(BaseSettings):
    PRIVATE_KEY: str
    PUBLIC_KEY: str
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    REFRESH_TOKEN_EXPIRE_DAYS:int
    TOKEN_HASH_KEY:str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

dbsettings= DBSettings()
settings = Settings()
