from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    service_name: str = "ms-analytics"
    service_version: str = "1.0.0"
    service_port: int = 8005
    environment: str = "dev"
    database_url: str = "postgresql://postgres:admin@db-postgres:5432/territorial_db"
    MS_CONFIGURATION_URL: str = "http://ms-configuration:8003"
    MS_TRANSFORMATION_URL: str = "http://ms-transformation:8004"
    MS_AUDIT_TRACE_URL: str = "http://ms-audit-trace:8002"


    class Config:
        env_file = ".env"
        extra = "ignore"  # <--- ESTA LÍNEA ES LA QUE ACTIVA EL PUERTO 8005
        case_sensitive = False # Recomendado para evitar errores de mayúsculas


settings = Settings()
