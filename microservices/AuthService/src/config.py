import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int

    WORKERS: int = 1
    SERVICE_PORT: int = 8001

    SECRET_KEY: str
    ALGORITHM: str

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str

    DEV_MODE: bool
    TOKEN_LIFETIME: int
    ACCESS_TOKEN: str = "access_token"

    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

    def get_db_url(self):
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    def get_redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


settings = Settings()
