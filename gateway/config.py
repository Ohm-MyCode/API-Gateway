from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PUBLIC_KEY: str
    JWT_ALGORITHM: str = "RS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
