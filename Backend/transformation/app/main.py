import time
import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.database import engine, init_db
from app.core.exceptions import global_exception_handler
from app.api.endpoints.transform import router as transformRouter

logger = logging.getLogger("TransformationService")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - [Trace: %(trace_id)s] - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

app = FastAPI(title="Transformation Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)


@app.middleware("http")
async def traceMiddleware(request: Request, call_next):
    traceId = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
    request.state.trace_id = traceId
    adapter = logging.LoggerAdapter(logger, {"trace_id": traceId})
    request.state.logger = adapter

    adapter.info(f"Received: {request.method} {request.url.path}")
    response = await call_next(request)
    response.headers["X-Trace-Id"] = traceId
    adapter.info(f"Response: {response.status_code}")
    return response


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/health")
def health():
    try:
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        dbConnected = True
    except Exception:
        dbConnected = False

    return {
        "status": "healthy" if dbConnected else "unhealthy",
        "service": "ms-transformation",
        "version": "1.0.0",
        "db_connected": dbConnected,
        "timestamp": int(time.time()),
    }


@app.get("/")
def root():
    return {
        "message": "Transformation Service is running",
        "version": "1.0.0",
        "docs": "/docs",
    }


app.include_router(transformRouter)
