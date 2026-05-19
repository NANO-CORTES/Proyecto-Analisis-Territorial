from __future__ import annotations

import csv
import io
import logging
import asyncio
import json
import base64
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

from app.core.config import settings

router = APIRouter(prefix="/api/bff", tags=["bff"])
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60.0


async def _safe_get(client: httpx.AsyncClient, url: str, headers: Dict[str, str]) -> Optional[Any]:
    try:
        response = await client.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        logger.warning("downstream %s responded %s", url, response.status_code)
        return None
    except httpx.HTTPError as exc:
        logger.warning("downstream %s failed: %s", url, exc)
        return None


async def _safe_post(
    client: httpx.AsyncClient,
    url: str,
    headers: Dict[str, str],
    payload: Dict[str, Any],
) -> Optional[Any]:
    try:
        response = await client.post(url, headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
        if response.status_code in {200, 201}:
            return response.json()
        return None
    except httpx.HTTPError as exc:
        logger.warning("downstream %s failed: %s", url, exc)
        return None


def _trace_headers(request: Request) -> Dict[str, str]:
    return {"x-trace-id": getattr(request.state, "trace_id", "")}


@router.get("/zone-summary/{zone_code}")
async def zone_summary(zone_code: str, request: Request):
    headers = _trace_headers(request)
    async with httpx.AsyncClient() as client:
        analytics = await _safe_get(
            client, f"{settings.MS_ANALYTICS_URL}/api/v1/zone-summary/{zone_code}", headers
        )
        recommendation = await _safe_get(
            client, f"{settings.MS_RECOMMENDATIONS_URL}/api/v1/recommendations/{zone_code}", headers
        )
        prediction_payload = await _safe_post(
            client,
            f"{settings.MS_ML_URL}/api/v1/ml/predict",
            headers,
            {"zone_codes": [zone_code]},
        )

    prediction = None
    if prediction_payload and prediction_payload.get("predictions"):
        prediction = prediction_payload["predictions"][0]

    partial = analytics is None or recommendation is None or prediction is None
    return {
        "zone_code": zone_code,
        "analytics": analytics,
        "recommendation": recommendation,
        "prediction": prediction,
        "partial": partial,
    }


@router.get("/compare")
async def compare_zones(
    request: Request,
    zones: str = Query(..., description="Comma separated zone codes (max 5)"),
):
    codes = [c.strip() for c in zones.split(",") if c.strip()][:5]
    if not codes:
        raise HTTPException(status_code=400, detail="zones is required")

    headers = _trace_headers(request)
    async with httpx.AsyncClient() as client:
        summaries = []
        for code in codes:
            data = await _safe_get(
                client, f"{settings.MS_ANALYTICS_URL}/api/v1/zone-summary/{code}", headers
            )
            summaries.append({"zone_code": code, "data": data})
        predictions_payload = await _safe_post(
            client,
            f"{settings.MS_ML_URL}/api/v1/ml/predict",
            headers,
            {"zone_codes": codes},
        )

    predictions_by_zone: Dict[str, Dict[str, Any]] = {}
    if predictions_payload:
        for item in predictions_payload.get("predictions", []):
            predictions_by_zone[item["zone_code"]] = item

    rows = []
    for entry in summaries:
        zone_code = entry["zone_code"]
        data = entry["data"] or {}
        score = data.get("score") or {}
        indicators = data.get("indicators") or {}
        prediction = predictions_by_zone.get(zone_code)
        rows.append({
            "zone_code": zone_code,
            "zone_name": score.get("zone_name") or zone_code,
            "indicators": indicators,
            "score_value": score.get("score_value"),
            "score_level": score.get("score_level"),
            "combined_score": score.get("combined_score"),
            "prediction_value": prediction.get("prediction_value") if prediction else None,
            "prediction_label": prediction.get("prediction_label") if prediction else None,
            "discrepancy_flag": score.get("discrepancy_flag"),
        })
    return {"total": len(rows), "zones": rows}


@router.get("/dashboard-summary")
async def dashboard_summary(
    request: Request,
    execution_id: str = Query(..., description="Scoring execution id"),
):
    headers = _trace_headers(request)
    async with httpx.AsyncClient() as client:
        ranking = await _safe_get(
            client,
            f"{settings.MS_ANALYTICS_URL}/api/v1/ranking?execution_id={execution_id}&page_size=1000",
            headers,
        )

    if not ranking:
        return JSONResponse(status_code=502, content={"error": "no ranking data"})

    items: List[Dict[str, Any]] = ranking.get("data", [])
    if not items:
        return {
            "total_zones_analyzed": 0,
            "avg_score": None,
            "top_zone": None,
            "score_distribution": {"ALTA": 0, "MEDIA": 0, "BAJA": 0},
        }

    avg = sum(i["score_value"] for i in items) / len(items)
    distribution = {"ALTA": 0, "MEDIA": 0, "BAJA": 0}
    for item in items:
        distribution[item.get("score_level", "BAJA")] = distribution.get(item.get("score_level", "BAJA"), 0) + 1
    top = max(items, key=lambda x: x.get("combined_score") or x.get("score_value", 0.0))
    return {
        "total_zones_analyzed": len(items),
        "avg_score": round(avg, 4),
        "top_zone": top,
        "score_distribution": distribution,
    }


@router.get("/export/ranking")
async def export_ranking(
    request: Request,
    execution_id: str = Query(...),
    fmt: str = Query("csv", alias="format"),
):
    headers = _trace_headers(request)
    async with httpx.AsyncClient() as client:
        ranking = await _safe_get(
            client,
            f"{settings.MS_ANALYTICS_URL}/api/v1/ranking?execution_id={execution_id}&page_size=10000",
            headers,
        )
    if not ranking:
        raise HTTPException(status_code=404, detail="ranking not found")

    items = ranking.get("data", [])
    if fmt == "json":
        return JSONResponse(content=items)

    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "rank_position",
            "zone_code",
            "zone_name",
            "score_value",
            "score_level",
            "combined_score",
            "prediction_value",
        ],
    )
    writer.writeheader()
    for item in items:
        writer.writerow({k: item.get(k) for k in writer.fieldnames})
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=ranking_{execution_id}.csv"},
    )


@router.get("/export/zone-report/{zone_code}")
async def export_zone_report(zone_code: str, request: Request):
    headers = _trace_headers(request)
    async with httpx.AsyncClient() as client:
        analytics = await _safe_get(
            client, f"{settings.MS_ANALYTICS_URL}/api/v1/zone-summary/{zone_code}", headers
        )
        recommendation = await _safe_get(
            client, f"{settings.MS_RECOMMENDATIONS_URL}/api/v1/recommendations/{zone_code}", headers
        )
    return {
        "zone_code": zone_code,
        "analytics": analytics,
        "recommendation": recommendation,
    }


def _extract_user_id_from_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return "system"

    token = auth_header.split(" ", 1)[1].strip()
    if token.count(".") < 2:
        return "system"

    try:
        payload_b64 = token.split(".", 2)[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8"))
    except Exception:
        return "system"

    user_id = payload.get("sub") or payload.get("user_id") or payload.get("username") or payload.get("email")
    return str(user_id) if user_id else "system"


async def _log_export_audit(request: Request, format_str: str, execution_id: str) -> None:
    user_id = _extract_user_id_from_token(request)
    payload = {
        "service_name": "bff-gateway",
        "action": "EXPORT_REPORT",
        "user_id": user_id,
        "details": json.dumps({
            "format": format_str,
            "execution_id": execution_id,
            "message": f"Exportado reporte territorial en formato {format_str} para la ejecucion {execution_id}"
        })
    }
    
    headers = _trace_headers(request)
    auth_header = request.headers.get("Authorization")
    if auth_header:
        headers["Authorization"] = auth_header
        
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.post(f"{settings.MS_AUDIT_TRACE_URL}/api/v1/audit/", json=payload, headers=headers)
    except Exception as e:
        logger.warning("Failed to log audit event to ms-audit-trace: %s", e)


@router.get("/latest-analysis")
async def get_latest_analysis(request: Request):
    headers = _trace_headers(request)
    auth_header = request.headers.get("Authorization")
    if auth_header:
        headers["Authorization"] = auth_header
    async with httpx.AsyncClient() as client:
        latest = await _safe_get(
            client, f"{settings.MS_ANALYTICS_URL}/api/v1/scoring/latest", headers
        )
    if not latest:
        return {"status": "NONE"}
    return latest


@router.get("/export/latest")
async def export_latest_analysis(
    request: Request,
    fmt: str = Query("csv", alias="format"),
):
    headers = _trace_headers(request)
    auth_header = request.headers.get("Authorization")
    if auth_header:
        headers["Authorization"] = auth_header

    async with httpx.AsyncClient() as client:
        # 1. Fetch latest analysis
        latest = await _safe_get(
            client, f"{settings.MS_ANALYTICS_URL}/api/v1/scoring/latest", headers
        )
        if not latest or latest.get("status") != "COMPLETED":
            raise HTTPException(status_code=400, detail="No hay un análisis territorial completado para exportar.")
        
        execution_id = latest["execution_id"]
        
        # 2. Get ranking/scores for this execution
        ranking = await _safe_get(
            client,
            f"{settings.MS_ANALYTICS_URL}/api/v1/ranking?execution_id={execution_id}&page_size=10000",
            headers,
        )
        if not ranking or not ranking.get("data"):
            raise HTTPException(status_code=404, detail="No se encontraron resultados para la última ejecución.")
        
        items = ranking["data"]
        
        # 3. Retrieve zone indicators, predictions, and recommendations in parallel for each zone
        zone_codes = [item["zone_code"] for item in items]
        
        async def fetch_zone_summary(code):
            return await _safe_get(client, f"{settings.MS_ANALYTICS_URL}/api/v1/zone-summary/{code}", headers)
            
        async def fetch_zone_rec(code):
            return await _safe_get(client, f"{settings.MS_RECOMMENDATIONS_URL}/api/v1/recommendations/{code}", headers)

        # Batch fetch predictions
        predictions_payload = await _safe_post(
            client,
            f"{settings.MS_ML_URL}/api/v1/ml/predict",
            headers,
            {"zone_codes": zone_codes},
        )
        predictions_by_zone = {}
        if predictions_payload and predictions_payload.get("predictions"):
            for pred in predictions_payload["predictions"]:
                predictions_by_zone[pred["zone_code"]] = pred
        
        # Parallel fetches for summaries and recs
        summary_tasks = [fetch_zone_summary(code) for code in zone_codes]
        rec_tasks = [fetch_zone_rec(code) for code in zone_codes]
        
        summaries = await asyncio.gather(*summary_tasks)
        recommendations = await asyncio.gather(*rec_tasks)
        
        consolidated = []
        for idx, code in enumerate(zone_codes):
            sum_data = summaries[idx] or {}
            rec_data = recommendations[idx] or {}
            pred_data = predictions_by_zone.get(code) or {}
            
            ind_data = sum_data.get("indicators") or {}
            score_data = sum_data.get("score") or {}
            
            score_value = score_data.get("score_value") if score_data else None
            score_level = score_data.get("score_level") if score_data else None
            combined_score = score_data.get("combined_score") if score_data else None
            discrepancy_flag = score_data.get("discrepancy_flag") if score_data else 0
            
            poblacion = ind_data.get("population_indicator") or 0.0
            ingreso = ind_data.get("income_indicator") or 0.0
            educacion = ind_data.get("education_indicator") or 0.0
            competencia = ind_data.get("competition_indicator") or 0.0
            
            prediction_value = pred_data.get("prediction_value")
            prediction_label = pred_data.get("prediction_label")
            
            fortalezas = rec_data.get("fortalezas") or []
            riesgos = rec_data.get("riesgos") or []
            explicacion = rec_data.get("explicacion") or sum_data.get("recommendation") or ""
            
            consolidated.append({
                "zone_code": code,
                "zone_name": score_data.get("zone_name") or sum_data.get("zone_name") or code,
                "score": {
                    "score_value": score_value,
                    "score_level": score_level,
                    "combined_score": combined_score,
                    "discrepancy_flag": discrepancy_flag,
                },
                "indicators": {
                    "poblacion": poblacion,
                    "ingreso": ingreso,
                    "educacion": educacion,
                    "competencia": competencia,
                },
                "prediction": {
                    "prediction_value": prediction_value,
                    "prediction_label": prediction_label,
                },
                "recommendation": {
                    "fortalezas": fortalezas,
                    "riesgos": riesgos,
                    "explicacion": explicacion,
                    "recommendation_level": rec_data.get("recommendation_level") or score_level or "BAJA",
                }
            })

        if fmt == "json":
            await _log_export_audit(request, "JSON", execution_id)
            json_bytes = json.dumps(consolidated, indent=2, ensure_ascii=False).encode("utf-8")
            return Response(
                content=json_bytes,
                media_type="application/json; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=analisis_territorial_{execution_id}.json"},
            )

        if fmt == "csv":
            buffer = io.StringIO()
            headers_csv = [
                "Código Zona", "Nombre Zona", "Indicador Población", "Indicador Ingreso",
                "Indicador Educación", "Indicador Competencia", "Score", "Nivel de Score",
                "Score Combinado", "Valor de Predicción ML", "Etiqueta de Predicción ML",
                "Alerta de Discrepancia", "Explicación Recomendación", "Fortalezas", "Riesgos"
            ]
            
            writer = csv.writer(buffer, delimiter=';')
            writer.writerow(headers_csv)
            
            for item in consolidated:
                forts = ", ".join(item["recommendation"]["fortalezas"]) if isinstance(item["recommendation"]["fortalezas"], list) else str(item["recommendation"]["fortalezas"])
                rgs = ", ".join(item["recommendation"]["riesgos"]) if isinstance(item["recommendation"]["riesgos"], list) else str(item["recommendation"]["riesgos"])
                
                writer.writerow([
                    item["zone_code"],
                    item["zone_name"],
                    item["indicators"]["poblacion"],
                    item["indicators"]["ingreso"],
                    item["indicators"]["educacion"],
                    item["indicators"]["competencia"],
                    item["score"]["score_value"],
                    item["score"]["score_level"],
                    item["score"]["combined_score"] if item["score"]["combined_score"] is not None else "",
                    item["prediction"]["prediction_value"] if item["prediction"]["prediction_value"] is not None else "",
                    item["prediction"]["prediction_label"] if item["prediction"]["prediction_label"] is not None else "",
                    "SI" if item["score"]["discrepancy_flag"] else "NO",
                    item["recommendation"]["explicacion"],
                    forts,
                    rgs
                ])
                
            content = buffer.getvalue()
            buffer.close()
            
            await _log_export_audit(request, "CSV", execution_id)
            
            bom = b'\xef\xbb\xbf'
            return Response(
                content=bom + content.encode("utf-8"),
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=analisis_territorial_{execution_id}.csv"},
            )

        if fmt == "xls":
            xls_content = """<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<style>
  table { border-collapse: collapse; font-family: Calibri, sans-serif; }
  th { background-color: #1F497D; color: #FFFFFF; font-weight: bold; border: 1px solid #95B3D7; padding: 6px; }
  td { border: 1px solid #95B3D7; padding: 6px; }
  .high { background-color: #E2EFDA; color: #375623; }
  .medium { background-color: #FFF2CC; color: #7F6000; }
  .low { background-color: #FCE4D6; color: #C65911; }
</style>
</head>
<body>
<table>
  <thead>
    <tr>
      <th>Código Zona</th>
      <th>Nombre Zona</th>
      <th>Indicador Población</th>
      <th>Indicador Ingreso</th>
      <th>Indicador Educación</th>
      <th>Indicador Competencia</th>
      <th>Score</th>
      <th>Nivel de Score</th>
      <th>Score Combinado</th>
      <th>Valor de Predicción ML</th>
      <th>Etiqueta de Predicción ML</th>
      <th>Alerta de Discrepancia</th>
      <th>Explicación Recomendación</th>
      <th>Fortalezas</th>
      <th>Riesgos</th>
    </tr>
  </thead>
  <tbody>
"""
            for item in consolidated:
                forts = ", ".join(item["recommendation"]["fortalezas"]) if isinstance(item["recommendation"]["fortalezas"], list) else str(item["recommendation"]["fortalezas"])
                rgs = ", ".join(item["recommendation"]["riesgos"]) if isinstance(item["recommendation"]["riesgos"], list) else str(item["recommendation"]["riesgos"])
                
                level_class = ""
                lvl = item["score"]["score_level"]
                if lvl == "ALTA":
                    level_class = ' class="high"'
                elif lvl == "MEDIA":
                    level_class = ' class="medium"'
                elif lvl == "BAJA":
                    level_class = ' class="low"'
                    
                xls_content += f"""    <tr>
      <td>{item["zone_code"]}</td>
      <td>{item["zone_name"]}</td>
      <td>{item["indicators"]["poblacion"]}</td>
      <td>{item["indicators"]["ingreso"]}</td>
      <td>{item["indicators"]["educacion"]}</td>
      <td>{item["indicators"]["competencia"]}</td>
      <td>{item["score"]["score_value"]}</td>
      <td{level_class}>{item["score"]["score_level"]}</td>
      <td>{item["score"]["combined_score"] if item["score"]["combined_score"] is not None else ""}</td>
      <td>{item["prediction"]["prediction_value"] if item["prediction"]["prediction_value"] is not None else ""}</td>
      <td>{item["prediction"]["prediction_label"] if item["prediction"]["prediction_label"] is not None else ""}</td>
      <td>{"SI" if item["score"]["discrepancy_flag"] else "NO"}</td>
      <td>{item["recommendation"]["explicacion"]}</td>
      <td>{forts}</td>
      <td>{rgs}</td>
    </tr>
"""
            xls_content += """  </tbody>
</table>
</body>
</html>"""
            
            await _log_export_audit(request, "XLS", execution_id)
            
            return Response(
                content=xls_content.encode("utf-8"),
                media_type="application/vnd.ms-excel; charset=utf-8",
                headers={"Content-Disposition": f"attachment; filename=analisis_territorial_{execution_id}.xls"},
            )

        raise HTTPException(status_code=400, detail=f"Formato {fmt} no soportado.")

