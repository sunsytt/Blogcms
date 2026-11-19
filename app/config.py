from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://cms:cms@localhost:5432/cms"
    use_mocks: bool = True
    builder_url: str = "http://localhost:8001"
    metrics_url: str = "http://localhost:8002/graphql"
    http_timeout_seconds: float = 60.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
