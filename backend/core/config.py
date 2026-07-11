"""
Application configuration using pydantic-settings
Reads from .env file automatically
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./resume_ai.db"

    # JWT Auth
    SECRET_KEY: str = "change-this-secret-key-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # HuggingFace
    HUGGINGFACE_API_KEY: str = ""
    HF_LLM_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"
    HF_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # LLM Provider
    LLM_PROVIDER: str = "huggingface"
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./vector_db/chroma_store"
    CHROMA_COLLECTION_NAME: str = "resume_embeddings"

    # File paths
    UPLOAD_DIR: str = "./uploads"
    REPORTS_DIR: str = "./reports"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8501", "http://localhost:3000", "*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)
