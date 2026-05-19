from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.health import router as health_router
from app.api.routers.recommendations import router as recommendations_router
from app.core.config import settings
from app.core.database import init_db

app = FastAPI(
    title=settings.service_name,
    description="Recommendation generation microservice",
    version=settings.service_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(recommendations_router)

@app.on_event("startup")
async def startup() -> None:
    try:
        init_db()
    except Exception as e:
        print(f"[WARNING] Database initialization failed: {e}")
        print("[INFO] Service starting anyway")

@app.get("/")
def root():
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "docs": "/docs",
    }

