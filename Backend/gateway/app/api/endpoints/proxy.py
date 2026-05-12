import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.core.config import settings
import logging

router = APIRouter()
client = httpx.AsyncClient()


async def forwardRequest(request: Request, destinationUrl: str):
    traceId = getattr(request.state, "trace_id", "")

    headers = dict(request.headers)
    headers["x-trace-id"] = traceId
    if "host" in headers:
        del headers["host"]

    try:
        proxyReq = client.build_request(
            method=request.method,
            url=destinationUrl,
            headers=headers,
            content=request.stream(),
        )
        response = await client.send(proxyReq, stream=True)
        return StreamingResponse(
            response.aiter_raw(),
            status_code=response.status_code,
            headers=dict(response.headers),
        )
    except httpx.RequestError as exc:
        logger = getattr(request.state, "logger", None)
        errorMsg = f"Downstream connection error to {destinationUrl} ({request.method} {request.url.path}): {exc}"
        if logger:
            logger.error(errorMsg)
        else:
            logging.getLogger("GatewayProxy").error(errorMsg)
        raise HTTPException(
            status_code=502,
            detail=f"Bad Gateway: unreachable {destinationUrl}. Check if the microservice is running.",
        )


@router.api_route("/configuration/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxyConfiguration(request: Request, path: str):
    url = f"{settings.MS_CONFIGURATION_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forwardRequest(request, url)


@router.api_route("/ingestion/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxyIngestion(request: Request, path: str):
    url = f"{settings.MS_INGESTION_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forwardRequest(request, url)


@router.api_route("/audit/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxyAudit(request: Request, path: str):
    url = f"{settings.MS_AUDIT_TRACE_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forwardRequest(request, url)


@router.api_route("/transformation/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxyTransformation(request: Request, path: str):
    url = f"{settings.MS_TRANSFORMATION_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forwardRequest(request, url)


@router.api_route("/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxyAnalytics(request: Request, path: str):
    url = f"{settings.MS_ANALYTICS_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forwardRequest(request, url)


@router.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxyAuth(request: Request, path: str):
    url = f"{settings.MS_AUTH_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forwardRequest(request, url)


@router.api_route("/admin/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxyAdmin(request: Request, path: str):
    url = f"{settings.MS_AUTH_URL}/admin/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forwardRequest(request, url)


@router.api_route("/ml/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxyMl(request: Request, path: str):
    url = f"{settings.MS_ML_URL}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
    return await forwardRequest(request, url)


@router.get("/bff/zone-summary/{zone_code}", tags=["bff"])
async def getZoneSummary(zone_code: str, request: Request):
    traceId = getattr(request.state, "trace_id", "")
    headers = {"x-trace-id": traceId}

    analyticsUrl = f"{settings.MS_ANALYTICS_URL}/api/v1/zone-summary/{zone_code}"

    async with httpx.AsyncClient() as c:
        try:
            resp = await c.get(analyticsUrl, headers=headers)

            if resp.status_code != 200:
                return JSONResponse(
                    status_code=resp.status_code,
                    content={"error": "Error al obtener datos de analítica", "partial": True},
                )

            data = resp.json()
            return data

        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Error de orquestación: {str(e)}", "partial": True},
            )
