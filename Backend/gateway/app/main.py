import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import proxy
from app.core.auth_middleware import auth_middleware
from app.core.middleware import GatewayTraceMiddleware

app = FastAPI(title="BFF API Gateway")


@app.middleware("http")
async def wrapAuthMiddleware(request: Request, call_next):
    try:
        return await auth_middleware(request, call_next)
    except Exception as e:
        trace_id = getattr(request.state, "trace_id", "")
        return JSONResponse(status_code=500, content={"error": "Gateway Error", "trace_id": trace_id})


app.add_middleware(GatewayTraceMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://[::1]:5173",
        "http://[::1]:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proxy.router, prefix="/api/v1", tags=["proxy"])


@app.get("/health")
def healthCheck():
    return {
        "status": "healthy",
        "service_name": "bff-gateway",
        "version": "1.0.0",
        "db_connected": False,
        "timestamp": int(time.time()),
    }
