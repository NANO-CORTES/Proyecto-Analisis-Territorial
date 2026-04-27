import httpx
import uuid
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.ranking import ZoneScore, ScoreExecution, ScoreLevel, IndicatorResult
from app.services.audit_client import send_trace_event

logger = logging.getLogger("ScoringService")

class ScoringService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def execute_scoring(self, transformation_run_id: str, db: Session) -> ScoreExecution:
        """
        HU-15: Ejecuta el motor de scoring territorial.
        1. Obtiene indicadores calculados (HU-13).
        2. Obtiene configuración de pesos de ms-configuration.
        3. Aplica fórmula y clasifica.
        4. Persiste resultados.
        """
        # 1. Obtener indicadores de la BD (asumimos que ya se calcularon y persistieron)
        indicators = db.query(IndicatorResult).filter(
            IndicatorResult.transformation_run_id == transformation_run_id
        ).all()
        
        if not indicators:
            logger.error(f"No indicators found for run {transformation_run_id}")
            raise Exception(f"No indicators found for run {transformation_run_id}. Run calculate first.")

        # 2. Obtener pesos de ms-configuration
        url = f"{settings.MS_CONFIGURATION_URL}/api/v1/config/scoring/active"
        resp = await self.client.get(url)
        if resp.status_code != 200:
            logger.warning("Could not fetch active config, using defaults")
            weights = {
                "population_weight": 0.25,
                "income_weight": 0.25,
                "education_weight": 0.25,
                "competition_weight": 0.25
            }
            config_id = "default"
        else:
            config_data = resp.json()
            weights = config_data
            config_id = config_data.get("id", "active")

        # 3. Crear ejecución
        execution = ScoreExecution(
            id=str(uuid.uuid4()),
            transformation_run_id=transformation_run_id,
            configuration_id=config_id,
            total_zones=len(indicators)
        )
        db.add(execution)

        # 4. Calcular scores
        zone_scores = []
        for ind in indicators:
            # Score = (w1*pob) + (w2*ing) + (w3*edu) - (w4*comp)
            score_val = (
                (weights["population_weight"] * ind.population_indicator) +
                (weights["income_weight"] * ind.income_indicator) +
                (weights["education_weight"] * ind.education_indicator) -
                (weights["competition_weight"] * ind.competition_indicator)
            )
            
            # Normalizar score final a [0, 1] si es necesario (según HU-15 dice entre 0 y 1)
            # En la práctica, si los pesos suman 1 y los indicadores están en [0,1], 
            # el resultado está entre -1 y 1. Lo ajustaremos a 0 si es negativo.
            score_val = max(0.0, min(1.0, score_val))

            # Clasificar
            level = ScoreLevel.BAJA
            if score_val > 0.7:
                level = ScoreLevel.ALTA
            elif score_val >= 0.4:
                level = ScoreLevel.MEDIA
            
            zone_scores.append({
                "zone_code": ind.zone_code,
                "zone_name": ind.zone_name,
                "score_value": score_val,
                "score_level": level
            })

        # Ordenar para asignar rank_position
        zone_scores.sort(key=lambda x: x["score_value"], reverse=True)
        
        db_scores = []
        for i, zs in enumerate(zone_scores):
            db_scores.append(ZoneScore(
                execution_id=execution.id,
                zone_code=zs["zone_code"],
                zone_name=zs["zone_name"],
                score_value=zs["score_value"],
                score_level=zs["score_level"],
                rank_position=i + 1
            ))

        db.add_all(db_scores)
        db.commit()
        db.refresh(execution)

        # Trazabilidad (HU-19)
        send_trace_event({
            "event_type": "SCORING_EXECUTED",
            "dataset_load_id": "unknown", # Debería pasarse o inferirse
            "transformation_run_id": transformation_run_id,
            "score_execution_id": execution.id,
            "parameters": weights,
            "result_summary": {"total_zones": len(indicators)}
        })

        return execution
