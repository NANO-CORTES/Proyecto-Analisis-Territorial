from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.api.endpoints.profiles import router as profilesRouter
from app.api.endpoints.scoring import router as scoringRouter

app = FastAPI(
    title="Configuration Service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "healthy", "service": "ms-configuration"}


@app.get("/")
def root():
    return {"message": "Configuration Service is running"}


app.include_router(profilesRouter)
app.include_router(scoringRouter)
