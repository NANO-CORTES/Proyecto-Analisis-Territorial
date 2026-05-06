from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api.endpoints import experiments
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Creamos las tablas
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

app = FastAPI(title="ML Service API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(experiments.router, prefix="/api/v1/ml/experiments", tags=["experiments"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ms-ml"}
