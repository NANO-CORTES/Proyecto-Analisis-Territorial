#!/usr/bin/env python3
"""
Script de ejemplo para probar la integración de datos externos.
Demuestra cómo usar el servicio ExternalDataService.
"""

import asyncio
import json
from app.services.external_data_service import external_data_service

async def main():
    """Función principal con ejemplos"""
    
    print("=" * 70)
    print("EJEMPLOS DE INTEGRACIÓN DE DATOS EXTERNOS")
    print("=" * 70)
    
    # Ejemplo 1: Buscar datos de población en Bogotá - Chapinero
    print("\n1. BÚSQUEDA DE DATOS DE POBLACIÓN")
    print("-" * 70)
    result = await external_data_service.search_territorial_data(
        department="Bogota",
        municipality="Chapinero",
        variable="population"
    )
    print(f"✓ Variable: {result.get('variable')}")
    print(f"✓ Encontrados: {result.get('found')}")
    print(f"✓ Datasets en datos.gov.co: {len(result.get('sources', {}).get('datos_gov', []))}")
    print(f"✓ Datasets en Bogotá: {len(result.get('sources', {}).get('bogota', []))}")
    
    # Ejemplo 2: Obtener todos los indicadores
    print("\n2. OBTENER TODOS LOS INDICADORES")
    print("-" * 70)
    indicators = await external_data_service.get_municipality_indicators(
        department="Medellín",
        municipality="Laureles"
    )
    
    if "indicators" in indicators:
        for var_name, var_data in indicators["indicators"].items():
            found = var_data.get("found", False)
            status = "✓ Encontrado" if found else "✗ No encontrado"
            print(f"  {var_name.upper():15} {status}")
    
    # Ejemplo 3: Buscar datasets específicos
    print("\n3. BUSCAR DATASETS EN DATOS.GOV.CO")
    print("-" * 70)
    datasets = await external_data_service.search_datasets(
        query="educación municipios",
        organization="datos_gov"
    )
    print(f"✓ Resultados encontrados: {len(datasets)}")
    if datasets:
        for ds in datasets[:2]:
            print(f"  • {ds.get('title', ds.get('name'))}")
            print(f"    Org: {ds.get('organization', {}).get('name')}")
            print(f"    Recursos: {len(ds.get('resources', []))}")
    
    # Ejemplo 4: Query CKAN personalizada
    print("\n4. QUERY CKAN PERSONALIZADA")
    print("-" * 70)
    ckan_data = await external_data_service.get_raw_ckan_data(
        organization="datos_gov",
        query="ingreso per cápita",
        dataset_type="dataset"
    )
    print(f"✓ Success: {ckan_data.get('success')}")
    print(f"✓ Total datasets: {ckan_data.get('total')}")
    print(f"✓ Datasets retornados: {len(ckan_data.get('datasets', []))}")
    
    # Ejemplo 5: Indicadores de múltiples municipios
    print("\n5. COMPARAR MÚLTIPLES MUNICIPIOS")
    print("-" * 70)
    municipalities = [
        ("Antioquia", "Medellín"),
        ("Valle del Cauca", "Cali"),
        ("Cundinamarca", "Bogotá D.C."),
    ]
    
    results = await asyncio.gather(*[
        external_data_service.get_municipality_indicators(dept, mun)
        for dept, mun in municipalities
    ])
    
    for (dept, mun), result in zip(municipalities, results):
        print(f"\n  {mun} ({dept})")
        if "indicators" in result:
            for var_name in ["population", "income", "education", "competition"]:
                found = result["indicators"][var_name].get("found", False)
                icon = "✓" if found else "✗"
                print(f"    {icon} {var_name}")
        elif "error" in result:
            print(f"    Error: {result['error']}")

    print("\n" + "=" * 70)
    print("EJEMPLOS COMPLETADOS")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
