from fastapi import FastAPI
from app.core.database import engine, Base
from app.api.endpoints import dataset
from app.api.endpoints.health import router as healthRouter
from app.core.middleware import TraceIdMiddleware
from app.core.exceptions import global_exception_handler
from sqlalchemy import text
import time

def initDbSchema():
    try:
        with engine.connect() as con:
            con.execute(text("CREATE SCHEMA IF NOT EXISTS ingestion"))
            con.commit()
            try:
                con.execute(text("ALTER TABLE ingestion.dataset_zones ADD COLUMN IF NOT EXISTS department VARCHAR"))
                con.commit()
            except Exception:
                pass
    except Exception as e:
        print(f"Error initializing schema: {e}")

initDbSchema()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ingestion Service",
    version="1.0.0",
)

app.add_exception_handler(Exception, global_exception_handler)
app.add_middleware(TraceIdMiddleware)

app.include_router(dataset.router, prefix="/datasets", tags=["datasets"])
app.include_router(healthRouter)


@app.get("/")
def root():
    return {"message": "Ingestion Service is running", "version": "1.0.0"}


@app.get("/health-check")
def healthCheck():
    try:
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        dbConnected = True
    except Exception:
        dbConnected = False

    return {
        "status": "healthy" if dbConnected else "unhealthy",
        "service_name": "ms-ingestion",
        "version": "1.0.0",
        "db_connected": dbConnected,
        "timestamp": int(time.time()),
    }
