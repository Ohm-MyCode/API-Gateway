from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
class DBSettings(BaseSettings):
    AUTH_DB:str
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

class Settings(BaseSettings):
    PRIVATE_KEY_PATH: str
    PUBLIC_KEY_PATH: str
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    REFRESH_TOKEN_EXPIRE_DAYS:int
    TOKEN_HASH_KEY:str

    @property
    def PRIVATE_KEY(self) -> str:
        return Path(self.PRIVATE_KEY_PATH).read_text()

    @property
    def PUBLIC_KEY(self) -> str:
        return Path(self.PUBLIC_KEY_PATH).read_text()

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

dbsettings= DBSettings()
settings = Settings()
