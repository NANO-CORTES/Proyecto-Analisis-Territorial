# Quick Start - Integración de Datos Externos

## ⚡ Inicio Rápido (5 minutos)

### 1️⃣ Verificar Dependencias

```bash
# Backend
pip list | grep httpx  # Debe estar instalado

# Frontend (ya está en package.json)
npm list axios
```

### 2️⃣ Iniciar Backend

```bash
cd Backend/ingestion
python -m uvicorn app.main:app --reload --port 8001
```

Respuesta esperada:
```
INFO:     Uvicorn running on http://127.0.0.1:8001
```

### 3️⃣ Verificar Health Check

```bash
curl http://localhost:8001/api/v1/external/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "services": {
    "datos_gov": "available",
    "bogota": "available"
  }
}
```

### 4️⃣ Prueba Rápida de API

```bash
# Obtener datos de población en Bogotá
curl "http://localhost:8001/api/v1/external/territorial-data?department=Bogota&municipality=Chapinero&variable=population"
```

### 5️⃣ Iniciar Frontend

```bash
cd Frontend/Frontend-Web
npm run dev
```

### 6️⃣ Usar en el Dashboard

1. Ve a Dashboard (login requerido)
2. Selecciona Departamento: "Cundinamarca"
3. Selecciona Municipio: "Bogota D.C."
4. **¡Verás la tarjeta con datos integrados!**

---

## 🧪 Pruebas Rápidas por Terminal

### Test 1: Buscar Datos de Población
```bash
curl -X GET "http://localhost:8001/api/v1/external/territorial-data?department=Antioquia&municipality=Medellin&variable=population" \
  -H "Content-Type: application/json"
```

### Test 2: Obtener Todos los Indicadores
```bash
curl -X GET "http://localhost:8001/api/v1/external/municipality-indicators?department=Valle%20del%20Cauca&municipality=Cali" \
  -H "Content-Type: application/json"
```

### Test 3: Buscar Datasets
```bash
curl -X GET "http://localhost:8001/api/v1/external/search-datasets?query=educacion&organization=datos_gov" \
  -H "Content-Type: application/json"
```

### Test 4: Query CKAN Personalizada
```bash
curl -X GET "http://localhost:8001/api/v1/external/ckan-query?query=competencia&organization=bogota" \
  -H "Content-Type: application/json"
```

---

## 🔬 Pruebas desde Python

```python
import asyncio
from Backend.ingestion.app.services.external_data_service import external_data_service

async def test():
    # Prueba 1: Buscar datos
    result = await external_data_service.search_territorial_data(
        "Bogota", "Chapinero", "population"
    )
    print(f"Encontrados: {result.get('found')}")
    
    # Prueba 2: Todos los indicadores
    indicators = await external_data_service.get_municipality_indicators(
        "Medellín", "Laureles"
    )
    print(f"Indicadores: {list(indicators['indicators'].keys())}")
    
    # Prueba 3: Buscar datasets
    datasets = await external_data_service.search_datasets(
        "ingreso per capita", "datos_gov"
    )
    print(f"Datasets encontrados: {len(datasets)}")

asyncio.run(test())
```

---

## 🎨 Pruebas desde React/TypeScript

```typescript
import { externalDataService } from './services/externalDataApi';

async function testIntegration() {
  try {
    // Prueba 1: Datos de población
    const popData = await externalDataService.getPopulationData(
      'Cundinamarca', 
      'Bogota D.C.'
    );
    console.log('Población:', popData);

    // Prueba 2: Todos los indicadores
    const allIndicators = await externalDataService.getMunicipalityIndicators(
      'Cundinamarca', 
      'Bogota D.C.'
    );
    console.log('Indicadores:', allIndicators);

    // Prueba 3: Búsqueda de datasets
    const searchResults = await externalDataService.searchDatasets(
      'educación', 
      'datos_gov'
    );
    console.log('Resultados:', searchResults);
  } catch (error) {
    console.error('Error:', error);
  }
}

// Ejecutar
testIntegration();
```

---

## 🚨 Problemas Comunes

### ❌ Error: "Connection refused"
```
Solución: Verifica que el backend esté ejecutándose en puerto 8001
```

### ❌ Error: "timeout"
```
Solución: CKAN puede estar lento. Intenta de nuevo. El timeout es 15s.
```

### ❌ Error: "No se encontraron datos"
```
Solución: 
- Verifica el nombre del departamento/municipio
- Intenta con otra variable
- Prueba con "Bogota" en lugar de "Bogotá"
```

### ❌ Error: "CORS error"
```
Solución: El backend debe tener CORS habilitado (ya está configurado)
```

---

## 📱 Ejemplo Completo en Frontend

```typescript
import React from 'react';
import TerritorialDataCard from './components/TerritorialDataCard';

export default function MyPage() {
  return (
    <div>
      <h1>Análisis Territorial</h1>
      
      {/* Componente que muestra datos automáticamente */}
      <TerritorialDataCard 
        department="Antioquia"
        municipality="Medellín"
      />
    </div>
  );
}
```

---

## 🔄 Flujo Completo en 30 Segundos

1. **Backend inicia** → `/api/v1/external/health` retorna "healthy"
2. **Frontend solicita** → `getMunicipalityIndicators("Bogota", "Chapinero")`
3. **Backend busca** → 4 tasks paralelos en CKAN (pop, income, edu, comp)
4. **Backend retorna** → JSON con datasets de ambas fuentes
5. **Frontend muestra** → TerritorialDataCard con tabs interactivos
6. **Usuario elige** → Cambiar entre población/ingreso/educación/competencia

---

## 📊 Datos Típicos Retornados

```json
{
  "success": true,
  "data": {
    "department": "Bogota",
    "municipality": "Chapinero",
    "indicators": {
      "population": {
        "found": true,
        "sources": {
          "datos_gov": [
            {
              "title": "Proyecciones de población",
              "organization": "DANE",
              "resources": [{"name": "...", "format": "CSV"}]
            }
          ],
          "bogota": [...]
        }
      },
      "income": {...},
      "education": {...},
      "competition": {...}
    }
  }
}
```

---

## 🆘 ¿Necesitas Ayuda?

### Para Backend:
```bash
# Ver logs detallados
python -m uvicorn app.main:app --reload --log-level debug
```

### Para Frontend:
```bash
# Ver console del navegador (F12)
# Buscar logs de "externalDataService"
```

### Para CKAN:
```bash
# Prueba directamente en el navegador:
https://www.datos.gov.co/api/3/package_search?q=población&rows=5
https://datosabiertos.bogota.gov.co/api/3/package_search?q=educación&rows=5
```

---

## ✅ Checklist de Verificación

- [ ] Backend ejecutándose en puerto 8001
- [ ] `/api/v1/external/health` retorna "healthy"
- [ ] Frontend puede conectar a backend
- [ ] TerritorialDataCard está importado en DashboardPage
- [ ] Selector de departamento/municipio funciona
- [ ] Tarjeta de datos aparece al seleccionar
- [ ] Puedo cambiar entre variables (población/ingreso/educación/competencia)
- [ ] Datos se cargan correctamente

---

## 🎯 Próximos Pasos

1. **Implementar caché** - Redis para datos
2. **Agregar gráficos** - Charts.js o D3.js
3. **Descargar datos** - CSV/JSON/GeoJSON
4. **Más variables** - Salud, seguridad, etc.
5. **API pública** - Para developers externos

---

**¡Listo para usar!** 🚀

Cualquier pregunta, revisa los docs en `/docs/EXTERNAL_DATA_INTEGRATION.md`
