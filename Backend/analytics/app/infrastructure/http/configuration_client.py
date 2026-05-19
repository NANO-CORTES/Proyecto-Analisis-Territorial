from __future__ import annotations

from typing import Tuple

import httpx

from app.core.config import settings
from app.domain.ports.configuration_provider import IConfigurationProvider
from app.domain.value_objects import CombinedWeights, ScoringWeights

class HttpConfigurationClient(IConfigurationProvider):
    def __init__(self, base_url: str = settings.MS_CONFIGURATION_URL, timeout: float = 5.0):
        self._base_url = base_url
        self._timeout = timeout

    async def get_active_weights(self) -> Tuple[str, ScoringWeights]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(f"{self._base_url}/api/v1/config/scoring/active")
        except httpx.HTTPError:
            return "default", ScoringWeights.default()

        if response.status_code != 200:
            return "default", ScoringWeights.default()

        payload = response.json()
        return str(payload.get("id", "active")), ScoringWeights.from_mapping(payload)

    async def get_combined_weights(self) -> CombinedWeights:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(f"{self._base_url}/api/v1/config/combined/active")
        except httpx.HTTPError:
            return CombinedWeights.default()

        if response.status_code != 200:
            return CombinedWeights.default()

        payload = response.json()
        return CombinedWeights(
            scoring=float(payload.get("scoring_weight", 0.6)),
            ml=float(payload.get("ml_weight", 0.4)),
        )
