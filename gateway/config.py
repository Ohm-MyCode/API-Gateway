from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    PUBLIC_KEY_PATH: str
    JWT_ALGORITHM: str = "RS256"

    @property
    def PUBLIC_KEY(self):
        return Path(self.PUBLIC_KEY_PATH).read_text()
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
