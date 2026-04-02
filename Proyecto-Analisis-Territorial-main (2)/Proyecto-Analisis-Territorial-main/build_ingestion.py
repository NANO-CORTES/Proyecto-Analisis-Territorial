import os
base_dir = r"c:\Users\User\Downloads\Proyecto-Analisis-Territorial-main"
ms_dir = os.path.join(base_dir, "Backend", "ingestion")

files = {
    "requirements.txt": """fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic
pydantic-settings
python-jose[cryptography]
python-multipart
pandas""",
    
    "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]""",
    
    "app/core/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ingestion Service"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()""",

    "app/core/database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()""",

    "app/core/security.py": """from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        return {"username": username, "role": role}
    except JWTError:
        raise credentials_exception""",

    "app/models/dataset.py": """from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base
from datetime import datetime

class DatasetLoad(Base):
    __tablename__ = "dataset_loads"
    __table_args__ = {'schema': 'ingestion'}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    file_name = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="UPLOADED")""",
    
    "app/main.py": """from fastapi import FastAPI, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import engine, Base, get_db
from app.core.security import get_current_user
from app.models.dataset import DatasetLoad

from sqlalchemy import text
with engine.connect() as con:
    con.execute(text("CREATE SCHEMA IF NOT EXISTS ingestion"))
    con.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ingestion Service")

@app.get("/health")
def health_check():
    return {"status": "healthy", "service_name": "ms-ingestion"}

@app.post("/api/v1/datasets/upload")
def upload_dataset(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Save metadata
    new_dataset = DatasetLoad(
        user_id=current_user["username"],
        file_name=file.filename,
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)
    
    return {
        "success": True,
        "data": {
            "dataset_id": new_dataset.id,
            "file_name": new_dataset.file_name,
            "uploaded_by": current_user["username"]
        }
    }"""
}

for filepath, content in files.items():
    full_path = os.path.join(ms_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip())

print("Ingestion MS built.")
