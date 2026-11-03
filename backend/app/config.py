from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    PORT: int
    DATABASE_URL: str
    JWT_SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    COOKIE_SECURE: bool
    REDIS_URL: str
    UPLOAD_DIR: str
    MAX_UPLOAD_BYTES: int
    CORS_ORIGINS: list[str]

app_settings = Settings()