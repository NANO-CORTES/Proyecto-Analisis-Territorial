import httpx
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.ranking import IndicatorResult, ZoneScore
import logging

logger = logging.getLogger("IndicatorsService")

class IndicatorsService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def calculate_indicators(self, transformation_run_id: str, db: Session) -> Dict[str, Any]:
        """
        HU-13: Calcula 4 indicadores base por zona.
        1. Obtiene resultados de ms-transformation.
        2. Agrupa por zona.
        3. Mapea columnas a indicadores específicos.
        """
        # 1. Obtener datos de ms-transformation
        url = f"{settings.MS_TRANSFORMATION_URL}/api/v1/transform/results/{transformation_run_id}"
        response = await self.client.get(url)
        
        if response.status_code != 200:
            logger.error(f"Error fetching transformation results: {response.text}")
            raise Exception(f"Failed to fetch transformation results: {response.status_code}")
            
        records = response.json()
        
        # 2. Agrupar por zona
        zones: Dict[str, Dict[str, Any]] = {}
        for rec in records:
            z_code = rec["zone_code"]
            if z_code not in zones:
                zones[z_code] = {
                    "zone_code": z_code,
                    "zone_name": rec["zone_name"],
                    "indicators": {}
                }
            
            col = rec["column_name"].lower()
            val = rec["normalized_value"]
            
            # Mapeo de columnas a indicadores (HU-13)
            if "population" in col or "poblacion" in col:
                zones[z_code]["indicators"]["population_indicator"] = val
            elif "income" in col or "ingreso" in col:
                zones[z_code]["indicators"]["income_indicator"] = val
            elif "education" in col or "educacion" in col:
                zones[z_code]["indicators"]["education_indicator"] = val
            elif "competition" in col or "competencia" in col:
                zones[z_code]["indicators"]["competition_indicator"] = val
            else:
                # Otros indicadores genéricos
                zones[z_code]["indicators"][f"{col}_indicator"] = val

        # 3. Asegurar que los 4 indicadores existan y persistir
        indicator_results = []
        for z_code, zone_data in zones.items():
            for ind in ["population_indicator", "income_indicator", "education_indicator", "competition_indicator"]:
                if ind not in zone_data["indicators"]:
                    zone_data["indicators"][ind] = 0.0
            
            res = IndicatorResult(
                transformation_run_id=transformation_run_id,
                zone_code=z_code,
                zone_name=zone_data["zone_name"],
                population_indicator=zone_data["indicators"]["population_indicator"],
                income_indicator=zone_data["indicators"]["income_indicator"],
                education_indicator=zone_data["indicators"]["education_indicator"],
                competition_indicator=zone_data["indicators"]["competition_indicator"]
            )
            indicator_results.append(res)
            db.add(res)

        db.commit()

        # Trazabilidad (HU-19)
        from app.services.audit_client import send_trace_event
        send_trace_event({
            "event_type": "INDICATORS_CALCULATED",
            "dataset_load_id": "unknown",
            "transformation_run_id": transformation_run_id,
            "result_summary": {"total_zones": len(zones)}
        })

        return {
            "transformation_run_id": transformation_run_id,
            "total_zones": len(zones),
            "zones": list(zones.values())
        }
