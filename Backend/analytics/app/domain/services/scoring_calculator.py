from __future__ import annotations

from typing import Iterable, List

from app.domain.entities import ZoneIndicators, ZoneScore
from app.domain.services.score_classifier import ScoreClassifier
from app.domain.value_objects import CombinedWeights, ScoringWeights

class ScoringCalculator:
    def __init__(self, classifier: ScoreClassifier):
        self._classifier = classifier

    def calculate(
        self,
        indicators: Iterable[ZoneIndicators],
        weights: ScoringWeights,
    ) -> List[ZoneScore]:
        scores: List[ZoneScore] = []
        for ind in indicators:
            raw = (
                weights.population * ind.population
                + weights.income * ind.income
                + weights.education * ind.education
                - weights.competition * ind.competition
            )
            value = self._clamp(raw)
            scores.append(
                ZoneScore(
                    zone_code=ind.zone_code,
                    zone_name=ind.zone_name,
                    score_value=value,
                    score_level=self._classifier.classify(value),
                )
            )
        return self._assign_ranks(scores)

    def combine(
        self,
        scores: List[ZoneScore],
        predictions: dict,
        weights: CombinedWeights,
        discrepancy_threshold: float = 0.3,
    ) -> List[ZoneScore]:
        for s in scores:
            prediction = predictions.get(s.zone_code)
            if prediction is None:
                continue
            s.prediction_value = prediction
            s.combined_score = self._clamp(
                weights.scoring * s.score_value + weights.ml * prediction
            )
            s.discrepancy_flag = abs(s.score_value - prediction) > discrepancy_threshold
        return scores

    def _assign_ranks(self, scores: List[ZoneScore]) -> List[ZoneScore]:
        scores.sort(key=lambda z: z.score_value, reverse=True)
        for position, zone in enumerate(scores, start=1):
            zone.rank_position = position
        return scores

    @staticmethod
    def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
        return max(lower, min(upper, value))
