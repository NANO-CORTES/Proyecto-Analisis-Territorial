from sqlalchemy.orm import Session
from app.models.scoring import ScoreExecution, ZoneScore
from app.schemas.scoring import ZoneScoreResult
from typing import List

class ScoringRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_execution(self, execution_id: str, results: List[ZoneScoreResult], transformation_run_id: str = "N/A", configuration_id: str = "N/A") -> ScoreExecution:
        # Create execution record
        execution = ScoreExecution(
            id=execution_id,
            transformation_run_id=transformation_run_id,
            configuration_id=configuration_id
        )
        self.db.add(execution)
        
        # Create zone scores
        zone_scores = [
            ZoneScore(
                execution_id=execution_id,
                zone_id=res.zone_id,
                score_value=res.score,
                score_level=res.classification
            )
            for res in results
        ]
        
        self.db.add_all(zone_scores)
        self.db.commit()
        
        return execution
