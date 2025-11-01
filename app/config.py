from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Elasticsearch
    elasticsearch_host: str = "http://localhost:9200"
    elasticsearch_user: str = "elastic"
    elasticsearch_password: str = "root"

    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_reload: bool = True

    # Index settings
    default_index: str = "documents"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
