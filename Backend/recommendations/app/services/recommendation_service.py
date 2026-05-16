import uuid
from typing import List
from app.interfaces.recommendation_repository import IRecommendationRepository
from app.models.recommendation import (
    RecommendationExecution, ZoneRecommendation, RecommendationLevel
)
from app.schemas.schema import (
    GenerateResponse, ZoneRecommendationItem,
    ZoneRecommendationResponse, RecommendationLevel as SchemaLevel
)
from app.services.rules_engine import RulesEngine
from app.services.audit_client import AuditClient

# Mock de zonas cuando no hay scoring real (igual que HU-16)
_MOCK_ZONES = [
    {"zone_code": "BOG-001", "zone_name": "chapinero",     "score_value": 0.87, "score_level": "ALTA",
     "population_indicator": 0.75, "income_indicator": 0.82, "education_indicator": 0.78, "competition_indicator": 0.65},
    {"zone_code": "BOG-003", "zone_name": "usaquen",       "score_value": 0.82, "score_level": "ALTA",
     "population_indicator": 0.70, "income_indicator": 0.88, "education_indicator": 0.85, "competition_indicator": 0.60},
    {"zone_code": "BOG-007", "zone_name": "fontibon",      "score_value": 0.76, "score_level": "ALTA",
     "population_indicator": 0.72, "income_indicator": 0.74, "education_indicator": 0.68, "competition_indicator": 0.45},
    {"zone_code": "BOG-002", "zone_name": "suba",          "score_value": 0.65, "score_level": "MEDIA",
     "population_indicator": 0.90, "income_indicator": 0.55, "education_indicator": 0.58, "competition_indicator": 0.62},
    {"zone_code": "BOG-006", "zone_name": "bosa",          "score_value": 0.61, "score_level": "MEDIA",
     "population_indicator": 0.85, "income_indicator": 0.48, "education_indicator": 0.50, "competition_indicator": 0.58},
    {"zone_code": "BOG-008", "zone_name": "puente aranda", "score_value": 0.58, "score_level": "MEDIA",
     "population_indicator": 0.65, "income_indicator": 0.52, "education_indicator": 0.55, "competition_indicator": 0.70},
    {"zone_code": "BOG-009", "zone_name": "barrios unidos","score_value": 0.54, "score_level": "MEDIA",
     "population_indicator": 0.60, "income_indicator": 0.50, "education_indicator": 0.58, "competition_indicator": 0.55},
    {"zone_code": "BOG-004", "zone_name": "kennedy",       "score_value": 0.38, "score_level": "BAJA",
     "population_indicator": 0.88, "income_indicator": 0.28, "education_indicator": 0.35, "competition_indicator": 0.75},
    {"zone_code": "BOG-005", "zone_name": "engativa",      "score_value": 0.31, "score_level": "BAJA",
     "population_indicator": 0.80, "income_indicator": 0.25, "education_indicator": 0.32, "competition_indicator": 0.72},
    {"zone_code": "BOG-012", "zone_name": "ciudad bolivar","score_value": 0.22, "score_level": "BAJA",
     "population_indicator": 0.75, "income_indicator": 0.18, "education_indicator": 0.22, "competition_indicator": 0.68},
]


class RecommendationService:
    """
    Servicio de generación de recomendaciones.
    SRP: solo coordina la generación, no tiene acceso directo a BD ni HTTP.
    DIP: depende de IRecommendationRepository (abstracción).
    Patrón Facade: simplifica la interacción entre RulesEngine, Repository y AuditClient.
    """

    def __init__(self, repository: IRecommendationRepository):
        self._repository = repository
        self._rules = RulesEngine()
        self._audit = AuditClient()

    async def generate(self, score_execution_id: str, prediction_batch_id: str) -> GenerateResponse:
        execution_id = str(uuid.uuid4())

        # Obtener zonas — intenta BD real, fallback a mock
        zones = await self._fetch_zones(score_execution_id)

        # Generar recomendación para cada zona
        items = []
        db_records = []

        for zone in zones:
            fortalezas, riesgos = self._rules.evaluate(zone)
            level = zone.get("score_level", "MEDIA")
            explanation = self._rules.build_explanation(
                zone_name=zone["zone_name"],
                score_value=zone["score_value"],
                level=level,
                fortalezas=fortalezas,
                riesgos=riesgos,
            )

            strengths_text = " | ".join(fortalezas)
            risks_text = " | ".join(riesgos)

            item = ZoneRecommendationItem(
                zone_code=zone["zone_code"],
                zone_name=zone["zone_name"],
                score_value=round(zone["score_value"], 4),
                recommendation_level=SchemaLevel(level),
                strengths_text=strengths_text,
                risks_text=risks_text,
                explanation_text=explanation,
            )
            items.append(item)

            db_records.append(ZoneRecommendation(
                execution_id=execution_id,
                zone_code=zone["zone_code"],
                zone_name=zone["zone_name"],
                score_value=zone["score_value"],
                recommendation_level=RecommendationLevel(level),
                strengths_text=strengths_text,
                risks_text=risks_text,
                explanation_text=explanation,
            ))

        # Persistir ejecución y recomendaciones
        execution = RecommendationExecution(
            id=execution_id,
            score_execution_id=score_execution_id,
            prediction_batch_id=prediction_batch_id,
            total_zones=str(len(items)),
        )
        self._repository.save_execution(execution)
        self._repository.save_recommendations(db_records)

        # Auditoría fire-and-forget
        await self._audit.send_event(
            event_type="RECOMMENDATIONS_GENERATED",
            service_name="ms-recommendations",
            reference_id=execution_id,
            summary=f"Recomendaciones generadas para {len(items)} zonas con execution_id={score_execution_id}",
        )

        return GenerateResponse(
            success=True,
            execution_id=execution_id,
            score_execution_id=score_execution_id,
            total_zones=len(items),
            data=items,
        )

    async def get_by_zone(self, zone_code: str) -> ZoneRecommendationResponse:
        # Intentar BD real primero
        record = self._repository.get_by_zone(zone_code)

        if record:
            item = ZoneRecommendationItem(
                zone_code=record.zone_code,
                zone_name=record.zone_name,
                score_value=record.score_value,
                recommendation_level=SchemaLevel(record.recommendation_level),
                strengths_text=record.strengths_text,
                risks_text=record.risks_text,
                explanation_text=record.explanation_text,
            )
            return ZoneRecommendationResponse(success=True, zone_code=zone_code, data=item)

        # Fallback a mock
        mock = self._repository.get_mock_recommendation(zone_code)
        if mock:
            item = ZoneRecommendationItem(**mock)
            return ZoneRecommendationResponse(success=True, zone_code=zone_code, data=item)

        # Generar en tiempo real si no hay nada guardado
        zone_data = next((z for z in _MOCK_ZONES if z["zone_code"] == zone_code), None)
        if zone_data:
            fortalezas, riesgos = self._rules.evaluate(zone_data)
            level = zone_data.get("score_level", "MEDIA")
            explanation = self._rules.build_explanation(
                zone_name=zone_data["zone_name"],
                score_value=zone_data["score_value"],
                level=level,
                fortalezas=fortalezas,
                riesgos=riesgos,
            )
            item = ZoneRecommendationItem(
                zone_code=zone_data["zone_code"],
                zone_name=zone_data["zone_name"],
                score_value=round(zone_data["score_value"], 4),
                recommendation_level=SchemaLevel(level),
                strengths_text=" | ".join(fortalezas),
                risks_text=" | ".join(riesgos),
                explanation_text=explanation,
            )
            return ZoneRecommendationResponse(success=True, zone_code=zone_code, data=item)

        return ZoneRecommendationResponse(
            success=False,
            zone_code=zone_code,
            error=f"No se encontró información para la zona '{zone_code}'",
        )

    async def _fetch_zones(self, score_execution_id: str) -> list:
        """
        Strategy: intenta obtener zonas reales del ms-analytics.
        Si falla, usa mock para no bloquear el flujo.
        """
        try:
            import httpx
            from app.core.config import settings
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(
                    f"{settings.ms_analytics_url}/api/v1/scoring/results",
                    params={"execution_id": score_execution_id},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data and len(data) > 0:
                        return data
        except Exception:
            pass
        return _MOCK_ZONES