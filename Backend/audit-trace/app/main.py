from fastapi import FastAPI
from app.core.database import init_db
from app.api.endpoints.trace import router as traceRouter

app = FastAPI(title="Audit Trace Service")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    return {"message": "Audit Trace Service running"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "audit-trace"}


app.include_router(traceRouter)