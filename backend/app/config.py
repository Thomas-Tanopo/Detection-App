import os
from pydantic_settings import BaseSettings

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
STATIC_DIR = os.path.join(PROJECT_DIR, "static")
UPLOAD_DIR_ENV = "uploads"

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/detect_app"
    SECRET_KEY: str = "detect-app-secret-key-change-in-production"
    UPLOAD_DIR: str = "uploads"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
