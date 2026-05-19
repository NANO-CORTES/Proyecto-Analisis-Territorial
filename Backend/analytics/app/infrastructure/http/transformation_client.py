from __future__ import annotations

from typing import Any, Dict, List

import httpx

from app.core.config import settings
from app.domain.entities import ZoneIndicators
from app.domain.ports.transformation_provider import ITransformationProvider

class HttpTransformationClient(ITransformationProvider):
    _COLUMN_MAP = {
        "population": "population",
        "poblacion": "population",
        "income": "income",
        "ingreso": "income",
        "education": "education",
        "educacion": "education",
        "competition": "competition",
        "competencia": "competition",
    }

    def __init__(self, base_url: str = settings.MS_TRANSFORMATION_URL, timeout: float = 10.0):
        self._base_url = base_url
        self._timeout = timeout

    async def fetch_zone_indicators(self, transformation_run_id: str) -> List[ZoneIndicators]:
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{self._base_url}/api/v1/transform/results/{transformation_run_id}"
            )
        if response.status_code != 200:
            raise RuntimeError(
                f"transformation service responded {response.status_code}: {response.text}"
            )
        return self._aggregate(response.json())

    def _aggregate(self, records: List[Dict[str, Any]]) -> List[ZoneIndicators]:
        zones: Dict[str, ZoneIndicators] = {}
        for rec in records:
            zone_code = rec["zone_code"]
            zone = zones.setdefault(
                zone_code,
                ZoneIndicators(zone_code=zone_code, zone_name=rec.get("zone_name", "")),
            )
            indicator = self._map_column(rec.get("column_name", ""))
            if indicator is None:
                continue
            setattr(zone, indicator, float(rec.get("normalized_value", 0.0)))
        return list(zones.values())

    @classmethod
    def _map_column(cls, name: str) -> str | None:
        normalized = name.lower()
        for key, target in cls._COLUMN_MAP.items():
            if key in normalized:
                return target
        return None
