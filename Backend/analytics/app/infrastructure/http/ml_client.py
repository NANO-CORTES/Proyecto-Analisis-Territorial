from __future__ import annotations

import logging
from typing import Dict, Iterable

import httpx

from app.core.config import settings
from app.domain.ports.prediction_provider import IPredictionProvider

logger = logging.getLogger(__name__)

class HttpPredictionClient(IPredictionProvider):
    def __init__(self, base_url: str | None = None, timeout: float = 10.0):
        self._base_url = base_url or getattr(settings, "MS_ML_URL", "http://ms-ml:8006")
        self._timeout = timeout

    async def predict_for_zones(self, zone_codes: Iterable[str]) -> Dict[str, float]:
        codes = list(zone_codes)
        if not codes:
            return {}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/v1/ml/predict",
                    json={"zone_codes": codes},
                )
        except httpx.HTTPError as exc:
            logger.warning("ml client failed: %s", exc)
            return {}

        if response.status_code != 200:
            return {}

        payload = response.json()
        predictions = payload.get("predictions", payload.get("data", []))
        return {
            item["zone_code"]: float(item.get("prediction_value", 0.0))
            for item in predictions
            if "zone_code" in item
        }
