import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API configuration
    API_URL: str = "https://dummyjson.com/products"
    API_PAGE_LIMIT: int = 30
    API_TIMEOUT_SECONDS: int = 10

    # Database configuration: defaults to local SQLite for instant zero-setup execution,
    # or can connect to PostgreSQL using: postgresql://user:password@localhost:5432/etl_db
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./etl.db")

    # App configuration
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
