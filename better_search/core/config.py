from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PODCAST_INDEX_API_KEY: str
    PODCAST_INDEX_API_SECRET: str

    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: str = Field(default="6379")

    CELERY_BROKER_URL: str = Field(default="redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://redis:6379/0")

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    OPENAI_API_KEY: str

    LOCAL_EMBEDDING_MODEL: str = (
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    SPARSE_EMBEDDING_MODEL: str = "Qdrant/bm25"

    QDRANT_BASE_URL: str = "http://host.docker.internal:6333"


settings = Settings()
