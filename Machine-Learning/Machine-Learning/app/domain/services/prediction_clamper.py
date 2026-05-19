from __future__ import annotations


class PredictionClamper:
    def clamp(self, value: float, lower: float = 0.0, upper: float = 1.0) -> float:
        return max(lower, min(upper, value))

    def confidence(self, value: float) -> float:
        clamped = self.clamp(value)
        return round(1.0 - abs(clamped - 0.5) * 2.0 * 0.0 + (clamped if clamped > 0.5 else 1 - clamped), 4)
