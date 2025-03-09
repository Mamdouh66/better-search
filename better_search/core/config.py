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


settings = Settings()
