from __future__ import annotations

import logging
from typing import Any, Mapping

import httpx

from app.core.config import settings
from app.domain.ports.audit_publisher import IAuditPublisher

logger = logging.getLogger(__name__)


class HttpAuditPublisher(IAuditPublisher):
    def __init__(self, base_url: str = settings.MS_AUDIT_TRACE_URL, timeout: float = 5.0):
        self._base_url = base_url
        self._timeout = timeout

    async def publish(self, event_type: str, payload: Mapping[str, Any]) -> bool:
        body = {"event_type": event_type, "service_name": settings.service_name, **payload}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/v1/events",
                    json=body,
                )
            return response.status_code in {200, 201, 202}
        except httpx.HTTPError as exc:
            logger.warning("audit publish failed: %s", exc)
            return False
