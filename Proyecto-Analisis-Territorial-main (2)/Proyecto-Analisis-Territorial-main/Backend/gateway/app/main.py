from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="API Gateway / BFF")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que cualquier puerto (como el 5173) se conecte
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, etc.
    allow_headers=["*"],  # Permite todos los headers
)
# Services mapping
SERVICES = {
    "configuration": "http://ms_configuration:8003",
    "ingestion": "http://ms_ingestion:8001",
    "audit-trace": "http://ms_audit-trace:8002"
}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service_name": "bff-gateway"}

async def forward_request(method: str, url: str, request: Request):
    headers = dict(request.headers)
    headers.pop("host", None) # Important when forwarding
    
    body = await request.body()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method,
                url,
                headers=headers,
                data=body,
                params=request.query_params
            )
            return JSONResponse(status_code=response.status_code, content=response.json())
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Error forwarding request: {str(exc)}")
        except Exception as e:
            # Fallback for multipart form or complex bodies without json
            return JSONResponse(status_code=response.status_code, content={"detail": response.text})

@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_auth(path: str, request: Request):
    return await forward_request(request.method, f"{SERVICES['configuration']}/{path}", request)

@app.api_route("/api/v1/datasets/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_ingestion(path: str, request: Request):
    return await forward_request(request.method, f"{SERVICES['ingestion']}/api/v1/datasets/{path}", request)

@app.api_route("/api/v1/events/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_audit(path: str, request: Request):
    return await forward_request(request.method, f"{SERVICES['audit-trace']}/api/v1/events/{path}", request)