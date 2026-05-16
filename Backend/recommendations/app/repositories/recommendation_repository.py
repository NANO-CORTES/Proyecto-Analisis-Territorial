from typing import List, Optional
from sqlalchemy.orm import Session
from app.interfaces.recommendation_repository import IRecommendationRepository
from app.models.recommendation import ZoneRecommendation, RecommendationExecution

# Datos mock — se usan cuando no hay scoring real disponible aún
_MOCK_RECOMMENDATIONS = {
    "BOG-001": {
        "zone_code": "BOG-001", "zone_name": "chapinero",
        "score_value": 0.87, "recommendation_level": "ALTA",
        "strengths_text": "Zona con alto potencial comercial. Presenta excelente nivel de ingreso de sus habitantes y alta densidad poblacional, lo que garantiza una base sólida de clientes potenciales. El nivel educativo de la zona favorece negocios de servicios especializados.",
        "risks_text": "Alta competencia de negocios similares ya establecidos en el sector. Se recomienda diferenciación clara del producto o servicio antes de ingresar al mercado.",
        "explanation_text": "Chapinero es una zona de ALTA oportunidad con score de 0.87. Su combinación de ingresos altos y buena educación la convierte en un mercado atractivo, aunque la competencia existente exige una propuesta de valor diferenciada.",
    },
    "BOG-002": {
        "zone_code": "BOG-002", "zone_name": "suba",
        "score_value": 0.65, "recommendation_level": "MEDIA",
        "strengths_text": "Zona con alta densidad poblacional que garantiza volumen de clientes potenciales. Buena conectividad vial y presencia de centros comerciales consolidados.",
        "risks_text": "Nivel de ingreso medio-bajo puede limitar el ticket promedio de compra. Alta competencia en segmentos de precio bajo.",
        "explanation_text": "Suba es una zona de MEDIA oportunidad con score de 0.65. Su gran población es una ventaja, pero el poder adquisitivo moderado requiere estrategias de precio ajustadas al mercado local.",
    },
    "BOG-004": {
        "zone_code": "BOG-004", "zone_name": "kennedy",
        "score_value": 0.38, "recommendation_level": "BAJA",
        "strengths_text": "Alta densidad poblacional con potencial para negocios de primera necesidad y servicios básicos.",
        "risks_text": "Bajo poder adquisitivo de sus habitantes limita significativamente el mercado. Alta competencia en productos de bajo costo. Indicadores educativos bajos reducen el mercado para servicios especializados.",
        "explanation_text": "Kennedy es una zona de BAJA oportunidad con score de 0.38. Si bien tiene mucha población, la combinación de bajo ingreso y alta competencia hace necesario un análisis muy detallado antes de invertir.",
    },
}


class RecommendationRepository(IRecommendationRepository):
    """
    Implementación concreta del repositorio.
    SRP: solo maneja acceso a datos de recomendaciones.
    LSP: cumple completamente el contrato de IRecommendationRepository.
    """

    def __init__(self, db):
        self._db = db

    def save_execution(self, execution: RecommendationExecution) -> RecommendationExecution:
        if self._db is None:
            return execution
        try:
            self._db.add(execution)
            self._db.commit()
            self._db.refresh(execution)
            return execution
        except Exception:
            self._db.rollback()
            return execution

    def save_recommendations(self, items: List[ZoneRecommendation]) -> List[ZoneRecommendation]:
        if self._db is None:
            return items
        try:
            for item in items:
                self._db.add(item)
            self._db.commit()
            return items
        except Exception:
            self._db.rollback()
            return items

    def get_by_zone(self, zone_code: str) -> Optional[ZoneRecommendation]:
        if self._db is None:
            return None
        try:
            return self._db.query(ZoneRecommendation).filter(
                ZoneRecommendation.zone_code == zone_code
            ).order_by(ZoneRecommendation.created_at.desc()).first()
        except Exception:
            return None

    def get_mock_recommendation(self, zone_code: str) -> Optional[dict]:
        return _MOCK_RECOMMENDATIONS.get(zone_code)