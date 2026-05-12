import httpx
import uuid
import logging
from app.core.config import settings
from app.models.ranking import ZoneScore, ScoreExecution, ScoreLevel
from app.services.audit_client import send_trace_event
from app.interfaces.ranking_repository import IRankingRepository
from app.interfaces.indicators_repository import IIndicatorsRepository

logger = logging.getLogger("ScoringService")


class ScoringService:
    def __init__(self, ranking_repo: IRankingRepository, indicators_repo: IIndicatorsRepository):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.ranking_repo = ranking_repo
        self.indicators_repo = indicators_repo

    async def execute_scoring(self, transformation_run_id: str) -> ScoreExecution:
        indicators = self.indicators_repo.get_by_run(transformation_run_id)

        if not indicators:
            logger.error(f"No indicators found for run {transformation_run_id}")
            raise Exception(f"No indicators found for run {transformation_run_id}. Run calculate first.")

        url = f"{settings.MS_CONFIGURATION_URL}/api/v1/config/scoring/active"
        try:
            resp = await self.client.get(url)
            if resp.status_code != 200:
                raise Exception("Config not found")
            config_data = resp.json()
            weights = config_data
            config_id = config_data.get("id", "active")
        except Exception:
            logger.warning("Could not fetch active config, using defaults")
            weights = {
                "population_weight": 0.25,
                "income_weight": 0.25,
                "education_weight": 0.25,
                "competition_weight": 0.25,
            }
            config_id = "default"

        execution = ScoreExecution(
            id=str(uuid.uuid4()),
            transformation_run_id=transformation_run_id,
            configuration_id=config_id,
            total_zones=len(indicators),
        )

        zone_scores = []
        for ind in indicators:
            score_val = (
                (weights["population_weight"] * ind.population_indicator)
                + (weights["income_weight"] * ind.income_indicator)
                + (weights["education_weight"] * ind.education_indicator)
                - (weights["competition_weight"] * ind.competition_indicator)
            )

            score_val = max(0.0, min(1.0, score_val))

            level = ScoreLevel.BAJA
            if score_val > 0.7:
                level = ScoreLevel.ALTA
            elif score_val >= 0.4:
                level = ScoreLevel.MEDIA

            zone_scores.append({
                "zone_code": ind.zone_code,
                "zone_name": ind.zone_name,
                "score_value": score_val,
                "score_level": level,
            })

        zone_scores.sort(key=lambda x: x["score_value"], reverse=True)

        db_scores = []
        for i, zs in enumerate(zone_scores):
            db_scores.append(ZoneScore(
                execution_id=execution.id,
                zone_code=zs["zone_code"],
                zone_name=zs["zone_name"],
                score_value=zs["score_value"],
                score_level=zs["score_level"],
                rank_position=i + 1,
            ))

        self.ranking_repo.create_execution(execution, db_scores)

        send_trace_event({
            "event_type": "SCORING_EXECUTED",
            "dataset_load_id": "unknown",
            "transformation_run_id": transformation_run_id,
            "score_execution_id": execution.id,
            "parameters": weights,
            "result_summary": {"total_zones": len(indicators)},
        })

        return execution
