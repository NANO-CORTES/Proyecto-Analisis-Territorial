from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.endpoints.recommendations import router as recommendations_router
from app.api.endpoints.health import router as health_router


app = FastAPI(
    title=settings.service_name,
    description="Microservicio de recomendaciones explicadas por zona territorial",
    version=settings.service_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations_router)
app.include_router(health_router)


@app.on_event("startup")
async def startup():
    try:
        from app.core.database import init_db
        init_db()
    except Exception as e:
        print(f"[WARNING] BD no disponible: {e}")
        print("[INFO] Servicio arranca con datos mock")


@app.get("/")
def root():
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "docs": "/docs",
    }