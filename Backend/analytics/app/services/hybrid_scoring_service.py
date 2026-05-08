import httpx
from pydantic import BaseModel
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class CombinedScoreRequest(BaseModel):
    zone_code: str
    score: float
    prediction_value: float

class HybridScoringService:
    async def get_weights(self) -> tuple[float, float]:
        """
        Llama a ms-configuration para obtener los pesos de analytic_weight y prediction_weight.
        Si falla, retorna los pesos por defecto.
        """
        analytic_weight = 0.6
        prediction_weight = 0.4
        
        try:
            async with httpx.AsyncClient() as client:
                url = f"{settings.MS_CONFIGURATION_URL}/api/v1/configurations/weights"
                resp = await client.get(url, timeout=2.0)
                if resp.status_code == 200:
                    data = resp.json()
                    analytic_weight = data.get("analytic_weight", analytic_weight)
                    prediction_weight = data.get("prediction_weight", prediction_weight)
        except Exception as e:
            logger.warning(f"No se pudo obtener pesos de configuración. Usando defaults. Error: {e}")
            
        return analytic_weight, prediction_weight

    async def calculate_combined(self, request: CombinedScoreRequest) -> dict:
        """
        Calcula combined_score = (score * 0.6) + (prediction_value * 0.4)
        Asigna requires_review = true si abs(score - prediction_value) > 0.3
        """
        analytic_weight, prediction_weight = await self.get_weights()
        
        combined_score = (request.score * analytic_weight) + (request.prediction_value * prediction_weight)
        
        requires_review = False
        if abs(request.score - request.prediction_value) > 0.3:
            requires_review = True
            
        return {
            "zone_code": request.zone_code,
            "original_score": request.score,
            "prediction_value": request.prediction_value,
            "combined_score": combined_score,
            "requires_review": requires_review
        }

