from __future__ import annotations

from app.domain.value_objects import ScoreLevel

class ScoreClassifier:
    HIGH_THRESHOLD = 0.7
    MEDIUM_THRESHOLD = 0.4

    def classify(self, score_value: float) -> ScoreLevel:
        if score_value > self.HIGH_THRESHOLD:
            return ScoreLevel.ALTA
        if score_value >= self.MEDIUM_THRESHOLD:
            return ScoreLevel.MEDIA
        return ScoreLevel.BAJA
