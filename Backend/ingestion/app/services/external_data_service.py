"""
Servicio para integrar datos de APIs externas (CKAN).
Consume datos de datos.gov.co y datosabiertos.bogota.gov.co
"""
import httpx
import asyncio
from typing import Optional, Dict, List, Any
import logging
from functools import lru_cache
import json

logger = logging.getLogger(__name__)

class ExternalDataService:
    """Servicio para consumir datos de portales CKAN públicos"""

    def __init__(self):
        self.datos_gov_base = "https://www.datos.gov.co/api/3"
        self.datos_abiertos_bogota_base = "https://datosabiertos.bogota.gov.co/api/3"
        self.timeout = httpx.Timeout(15.0)
        
        # Mapeo de variables a keywords de búsqueda en CKAN
        self.variable_keywords = {
            "population": ["población", "population", "habitantes", "demográfico"],
            "income": ["ingreso", "ingresos", "income", "salario", "remuneración", "económico"],
            "education": ["educación", "education", "escolaridad", "analfabetismo", "cobertura educativa"],
            "competition": ["competencia", "competition", "empresas", "actividad económica", "competitiva"]
        }

    async def search_datasets(self, query: str, organization: str = "datos_gov") -> List[Dict[str, Any]]:
        """Busca datasets en el portal especificado"""
        try:
            if organization == "bogota":
                base_url = self.datos_abiertos_bogota_base
            else:
                base_url = self.datos_gov_base

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{base_url}/package_search",
                    params={"q": query, "rows": 20}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("result", {}).get("results", [])
        except Exception as e:
            logger.error(f"Error searching datasets in {organization}: {e}")
            return []

    async def get_resource_data(self, resource_url: str, format_type: str = "csv") -> Optional[Dict]:
        """Obtiene datos de un recurso específico"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(resource_url)
                response.raise_for_status()
                
                if format_type.lower() == "csv":
                    import pandas as pd
                    import io
                    df = pd.read_csv(io.StringIO(response.text))
                    return {
                        "data": df.to_dict('records')[:1000],  # Primeros 1000 registros
                        "columns": df.columns.tolist(),
                        "rows": len(df)
                    }
                elif format_type.lower() == "json":
                    return response.json()
                else:
                    return {"raw": response.text}
        except Exception as e:
            logger.error(f"Error getting resource data: {e}")
            return None

    async def search_territorial_data(
        self, 
        department: str, 
        municipality: str,
        variable: str = "population"
    ) -> Dict[str, Any]:
        """
        Busca datos territoriales específicos para una variable.
        Variables: population, income, education, competition
        """
        try:
            # Construir query de búsqueda
            query = f"{variable} {department} {municipality}"
            
            # Buscar en ambos portales en paralelo
            tasks = [
                self.search_datasets(query, "datos_gov"),
                self.search_datasets(query, "bogota")
            ]
            results = await asyncio.gather(*tasks)
            
            datasets_gov, datasets_bogota = results
            
            # Procesar resultados
            processed_data = {
                "variable": variable,
                "department": department,
                "municipality": municipality,
                "sources": {
                    "datos_gov": self._process_datasets(datasets_gov),
                    "bogota": self._process_datasets(datasets_bogota)
                },
                "found": len(datasets_gov) + len(datasets_bogota) > 0
            }
            
            return processed_data
        except Exception as e:
            logger.error(f"Error searching territorial data: {e}")
            return {
                "error": str(e),
                "variable": variable,
                "department": department,
                "municipality": municipality,
                "found": False
            }

    def _process_datasets(self, datasets: List[Dict]) -> List[Dict]:
        """Procesa los datasets para extraer información relevante"""
        processed = []
        for ds in datasets[:5]:  # Máximo 5 datasets por fuente
            processed.append({
                "id": ds.get("id"),
                "name": ds.get("name"),
                "title": ds.get("title"),
                "notes": ds.get("notes", "")[:200],  # Resumen de descripción
                "organization": ds.get("organization", {}).get("name"),
                "resources": [
                    {
                        "id": r.get("id"),
                        "name": r.get("name"),
                        "format": r.get("format"),
                        "url": r.get("url"),
                        "created": r.get("created")
                    }
                    for r in ds.get("resources", [])[:3]  # Máximo 3 recursos
                ],
                "metadata_created": ds.get("metadata_created"),
                "metadata_modified": ds.get("metadata_modified")
            })
        return processed

    async def get_municipality_indicators(
        self, 
        department: str, 
        municipality: str
    ) -> Dict[str, Any]:
        """
        Obtiene todos los indicadores (población, ingreso, educación, competencia)
        para un municipio específico
        """
        try:
            tasks = [
                self.search_territorial_data(department, municipality, "population"),
                self.search_territorial_data(department, municipality, "income"),
                self.search_territorial_data(department, municipality, "education"),
                self.search_territorial_data(department, municipality, "competition")
            ]
            
            results = await asyncio.gather(*tasks)
            
            return {
                "department": department,
                "municipality": municipality,
                "indicators": {
                    "population": results[0],
                    "income": results[1],
                    "education": results[2],
                    "competition": results[3]
                },
                "fetched_at": str(asyncio.get_event_loop().time())
            }
        except Exception as e:
            logger.error(f"Error getting municipality indicators: {e}")
            return {
                "error": str(e),
                "department": department,
                "municipality": municipality
            }

    async def get_raw_ckan_data(
        self, 
        organization: str = "datos_gov",
        query: str = "",
        dataset_type: str = "dataset"
    ) -> Dict[str, Any]:
        """
        Obtiene datos crudos del CKAN API directamente.
        Útil para queries personalizadas.
        """
        try:
            base_url = (
                self.datos_abiertos_bogota_base 
                if organization == "bogota" 
                else self.datos_gov_base
            )
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "q": query,
                    "rows": 50,
                    "type": dataset_type
                }
                
                response = await client.get(
                    f"{base_url}/package_search",
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                return {
                    "success": data.get("success", True),
                    "total": data.get("result", {}).get("count", 0),
                    "datasets": data.get("result", {}).get("results", []),
                    "organization": organization
                }
        except Exception as e:
            logger.error(f"Error fetching raw CKAN data: {e}")
            return {
                "success": False,
                "error": str(e),
                "organization": organization
            }

# Instancia global del servicio
external_data_service = ExternalDataService()
