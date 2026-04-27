import httpx
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.core.config import settings
from typing import Optional

router = APIRouter()
client = httpx.AsyncClient()

async def forward_request(request: Request, destination_url: str):
    trace_id = getattr(request.state, "trace_id", "")
    
    headers = dict(request.headers)
    headers["x-trace-id"] = trace_id
    if "host" in headers:
        del headers["host"]
        
    try:
        proxy_req = client.build_request(
            method=request.method,
            url=destination_url,
            headers=headers,
            content=request.stream()
        )
        response = await client.send(proxy_req, stream=True)
        return StreamingResponse(
            response.aiter_raw(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.RequestError as exc:
        logger = getattr(request.state, "logger", None)
        error_msg = f"Downstream connection error to {destination_url} ({request.method} {request.url.path}): {exc}"
        if logger:
            logger.error(error_msg)
        else:
            # Fallback if logger is not in state
            import logging
            logging.getLogger("GatewayProxy").error(error_msg)
        raise HTTPException(
            status_code=502, 
            detail=f"Bad Gateway: unreachable {destination_url}. Check if the microservice is running."
        )

@router.api_route("/configuration/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_configuration(request: Request, path: str):
    url = f"{settings.MS_CONFIGURATION_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/ingestion/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_ingestion(request: Request, path: str):
    url = f"{settings.MS_INGESTION_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/audit/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_audit(request: Request, path: str):
    url = f"{settings.MS_AUDIT_TRACE_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/transformation/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_transformation(request: Request, path: str):
    url = f"{settings.MS_TRANSFORMATION_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_analytics(request: Request, path: str):
    url = f"{settings.MS_ANALYTICS_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_auth(request: Request, path: str):
    url = f"{settings.MS_AUTH_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.api_route("/admin/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_admin(request: Request, path: str):
    url = f"{settings.MS_AUTH_URL}/admin/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forward_request(request, url)

@router.get("/bff/zone-summary/{zone_code}", tags=["bff"])
async def get_zone_summary(zone_code: str, request: Request):
    """
    HU-17: Orquestación BFF.
    Consolida datos de ms-analytics (indicadores y score) para la UI.
    """
    trace_id = getattr(request.state, "trace_id", "")
    headers = {"x-trace-id": trace_id}
    
    analytics_url = f"{settings.MS_ANALYTICS_URL}/api/v1/zone-summary/{zone_code}"
    
    async with httpx.AsyncClient() as client:
        try:
            # En un caso real, aquí llamaríamos a múltiples servicios en paralelo
            # Por ahora, ms-analytics ya consolida indicadores y score de su propia BD
            resp = await client.get(analytics_url, headers=headers)
            
            if resp.status_code != 200:
                return JSONResponse(
                    status_code=resp.status_code,
                    content={"error": "Error al obtener datos de analítica", "partial": True}
                )
                
            data = resp.json()
            return data
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Error de orquestación: {str(e)}", "partial": True}
            )
