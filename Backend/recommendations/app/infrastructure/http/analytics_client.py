from __future__ import annotations

from typing import List

import httpx

from app.core.config import settings
from app.domain.entities import ZoneAnalytics
from app.domain.ports.analytics_provider import IAnalyticsProvider

class HttpAnalyticsClient(IAnalyticsProvider):
    def __init__(self, base_url: str = settings.MS_ANALYTICS_URL, timeout: float = 10.0):
        self._base_url = base_url
        self._timeout = timeout

    async def list_zone_results(self, score_execution_id: str) -> List[ZoneAnalytics]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            ranking = await client.get(
                f"{self._base_url}/api/v1/ranking",
                params={"execution_id": score_execution_id, "page_size": 1000},
            )
        if ranking.status_code != 200:
            raise RuntimeError(
                f"analytics ranking responded {ranking.status_code}: {ranking.text}"
            )
        payload = ranking.json()

        results: List[ZoneAnalytics] = []
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for item in payload.get("data", []):
                summary = await client.get(
                    f"{self._base_url}/api/v1/zone-summary/{item['zone_code']}"
                )
                indicators = summary.json().get("indicators") if summary.status_code == 200 else None
                results.append(
                    ZoneAnalytics(
                        zone_code=item["zone_code"],
                        zone_name=item["zone_name"],
                        score_value=float(item.get("score_value", 0.0)),
                        score_level=str(item.get("score_level", "BAJA")),
                        population_indicator=float(indicators.get("population_indicator", 0.0)) if indicators else 0.0,
                        income_indicator=float(indicators.get("income_indicator", 0.0)) if indicators else 0.0,
                        education_indicator=float(indicators.get("education_indicator", 0.0)) if indicators else 0.0,
                        competition_indicator=float(indicators.get("competition_indicator", 0.0)) if indicators else 0.0,
                        prediction_value=item.get("prediction_value"),
                    )
                )
        return results
