from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Elasticsearch
    elasticsearch_host: str = os.getenv("ELASTICSEARCH_HOST", "http://localhost:9200")
    elasticsearch_user: str = os.getenv("ELASTIC_USER", "elastic")
    elasticsearch_password: str = os.getenv("ELASTIC_PASSWORD", "changeme123")

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
