from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PODCAST_INDEX_API_KEY: str
    PODCAST_INDEX_API_SECRET: str

    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: str = Field(default="6379")

    CELERY_BROKER_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
    CELERY_RESULT_BACKEND: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"


settings = Settings()
