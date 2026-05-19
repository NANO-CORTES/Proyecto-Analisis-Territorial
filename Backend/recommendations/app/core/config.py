from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "ms-recommendations"
    service_version: str = "1.0.0"
    service_port: int = 8008
    environment: str = "dev"
    database_url: str = "postgresql://postgres:admin@localhost:5432/territorial_db"
    ms_analytics_url: str = "http://ms-analytics:8005"
    ms_audit_trace_url: str = "http://ms-audit-trace:8002"

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = False

settings = Settings()