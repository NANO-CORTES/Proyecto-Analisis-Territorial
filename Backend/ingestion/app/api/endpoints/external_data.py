"""
Endpoints para integración de datos externos de APIs CKAN.
Consume datos de datos.gov.co y datosabiertos.bogota.gov.co
"""
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks
from typing import Optional
from app.services.external_data_service import external_data_service
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/external", tags=["External Data Sources"])

@router.get("/territorial-data")
async def get_territorial_data(
    department: str = Query(..., description="Departamento"),
    municipality: str = Query(..., description="Municipio"),
    variable: Optional[str] = Query("population", description="Variable: population, income, education, competition")
):
    """
    Obtiene datos territoriales de APIs externas (CKAN).
    
    **Variables soportadas:**
    - population: Datos de población
    - income: Datos de ingreso
    - education: Datos de educación
    - competition: Datos de competencia/actividad económica
    """
    try:
        if variable not in ["population", "income", "education", "competition"]:
            raise HTTPException(
                status_code=400,
                detail="Variable no válida. Use: population, income, education, competition"
            )
        
        result = await external_data_service.search_territorial_data(
            department=department,
            municipality=municipality,
            variable=variable
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Error in get_territorial_data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/municipality-indicators")
async def get_municipality_indicators(
    department: str = Query(..., description="Departamento"),
    municipality: str = Query(..., description="Municipio")
):
    """
    Obtiene todos los indicadores (población, ingreso, educación, competencia)
    para un municipio específico desde múltiples fuentes de datos abiertos.
    """
    try:
        result = await external_data_service.get_municipality_indicators(
            department=department,
            municipality=municipality
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Error in get_municipality_indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search-datasets")
async def search_datasets(
    query: str = Query(..., description="Término de búsqueda"),
    organization: str = Query("datos_gov", description="datos_gov o bogota")
):
    """
    Busca datasets en los portales CKAN.
    
    **Organizaciones:**
    - datos_gov: Portal Nacional de Datos Abiertos (datos.gov.co)
    - bogota: Portal de Datos Abiertos de Bogotá
    """
    try:
        if organization not in ["datos_gov", "bogota"]:
            raise HTTPException(
                status_code=400,
                detail="Organización no válida. Use: datos_gov, bogota"
            )
        
        datasets = await external_data_service.search_datasets(query, organization)
        
        return {
            "success": True,
            "organization": organization,
            "query": query,
            "total": len(datasets),
            "datasets": datasets
        }
    except Exception as e:
        logger.error(f"Error in search_datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ckan-query")
async def ckan_query(
    query: str = Query("", description="Término de búsqueda CKAN"),
    organization: str = Query("datos_gov", description="datos_gov o bogota"),
    dataset_type: str = Query("dataset", description="Tipo de dataset")
):
    """
    Realiza una query directa a la API CKAN.
    Permite queries personalizadas y avanzadas.
    """
    try:
        result = await external_data_service.get_raw_ckan_data(
            organization=organization,
            query=query,
            dataset_type=dataset_type
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in ckan_query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check para el servicio de datos externos"""
    try:
        # Hacer una búsqueda rápida como prueba
        result = await external_data_service.search_datasets("población", "datos_gov")
        
        return {
            "status": "healthy" if result else "degraded",
            "services": {
                "datos_gov": "available" if result else "unavailable",
                "bogota": "available"  # Asumir disponible por defecto
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
