from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "development"
    #allowed_origins: List[str]
    log_level: str = "INFO"
    api_key: str 
    api_secret: str

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    return Settings() # type: ignore