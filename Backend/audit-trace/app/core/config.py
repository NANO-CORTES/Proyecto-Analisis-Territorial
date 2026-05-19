import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Usar PostgreSQL por defecto en la orquestación Docker, con fallback a SQLite local
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:admin@db-postgres:5432/territorial_db")
    SERVICE_NAME: str = "audit-trace"
    VERSION: str = "1.0.0"
    
    class Config:
        extra = "ignore"

settings = Settings()