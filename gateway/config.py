from functools import cached_property
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PUBLIC_KEY_PATH: str
    JWT_ALGORITHM: str = "RS256"
    redis_host:str="redis"
    redis_port:int=6379
    max_capacity:int=200
    refill_rate:int = 100

    @cached_property
    def PUBLIC_KEY(self):
        return Path(self.PUBLIC_KEY_PATH).read_text()
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )
    def lua_script(self) -> str:
        script_path = Path(__file__).parent / "script.lua"
        return script_path.read_text()
    
SERVICES = {
    "auth": "http://auth-service:8000",
    "url": "http://url-service:8000",
}

AUTH_ROUTES = {
    "/auth/login",
    "/auth/signup",
    "/auth/refresh",
    "/auth/logout",
    "/auth/logout-all"
}

settings = Settings()
