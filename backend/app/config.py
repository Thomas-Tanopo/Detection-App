import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/detect_app"
    SECRET_KEY: str = "detect-app-secret-key-change-in-production"
    UPLOAD_DIR: str = "uploads"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
