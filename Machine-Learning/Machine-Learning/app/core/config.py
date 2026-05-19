from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "ms-ml"
    service_version: str = "1.0.0"
    service_port: int = 8008
    environment: str = "dev"
    database_url: str = "postgresql://postgres:admin@db-postgres:5432/territorial_db"
    MS_AUDIT_TRACE_URL: str = "http://ms-audit-trace:8007"
    MS_ANALYTICS_URL: str = "http://ms-analytics:8006"
    MS_TRANSFORMATION_URL: str = "http://ms-transformation:8004"
    models_dir: str = "/app/storage/models"

    class Config:
        env_file = ".env"


settings = Settings()
