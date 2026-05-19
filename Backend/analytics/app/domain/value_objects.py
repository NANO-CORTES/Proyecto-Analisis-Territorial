from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

class ScoreLevel(str, Enum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"

@dataclass(frozen=True)
class ScoringWeights:
    population: float
    income: float
    education: float
    competition: float

    @classmethod
    def default(cls) -> "ScoringWeights":
        return cls(0.25, 0.25, 0.25, 0.25)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, float]) -> "ScoringWeights":
        return cls(
            population=float(raw.get("population_weight", 0.25)),
            income=float(raw.get("income_weight", 0.25)),
            education=float(raw.get("education_weight", 0.25)),
            competition=float(raw.get("competition_weight", 0.25)),
        )

@dataclass(frozen=True)
class CombinedWeights:
    scoring: float
    ml: float

    @classmethod
    def default(cls) -> "CombinedWeights":
        return cls(0.6, 0.4)
