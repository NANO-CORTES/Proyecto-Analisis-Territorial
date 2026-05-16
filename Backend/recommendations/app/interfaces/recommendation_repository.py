from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.recommendation import ZoneRecommendation, RecommendationExecution


class IRecommendationRepository(ABC):
    """
    Interfaz del repositorio de recomendaciones.
    DIP: servicios dependen de esta abstracción, no de la implementación.
    OCP: se puede extender con nuevas implementaciones sin tocar el servicio.
    """

    @abstractmethod
    def save_execution(self, execution: RecommendationExecution) -> RecommendationExecution:
        ...

    @abstractmethod
    def save_recommendations(self, items: List[ZoneRecommendation]) -> List[ZoneRecommendation]:
        ...

    @abstractmethod
    def get_by_zone(self, zone_code: str) -> Optional[ZoneRecommendation]:
        ...

    @abstractmethod
    def get_mock_recommendation(self, zone_code: str) -> Optional[dict]:
        ...