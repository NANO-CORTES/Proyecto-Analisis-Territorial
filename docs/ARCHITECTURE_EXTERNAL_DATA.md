# Arquitectura Técnica: Integración de Datos Externos

## 📐 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND (React/TypeScript)          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  DashboardPage (Selector Departamento/Municipio)     │   │
│  │  └─ TerritorialDataCard (Visualizar Datos)           │   │
│  │     └─ externalDataApi (Servicio HTTP)               │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────┬──────────────────────────────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  /api/v1/external/territorial-data                   │   │
│  │  /api/v1/external/municipality-indicators            │   │
│  │  /api/v1/external/search-datasets                    │   │
│  │  /api/v1/external/ckan-query                         │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────┬──────────────────────────────────────────────┘
               │ FastAPI/AsyncIO
┌──────────────▼──────────────────────────────────────────────┐
│              INGESTION SERVICE (Python)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  external_data_service.py                            │   │
│  │  ├─ search_territorial_data()                        │   │
│  │  ├─ get_municipality_indicators()                    │   │
│  │  ├─ search_datasets()                                │   │
│  │  └─ get_raw_ckan_data()                              │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────┬──────────────────────────────────────────────┘
               │ HTTPX (Async HTTP Client)
┌──────────────▼────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES (CKAN)                        │
│  ┌────────────────────────┐      ┌──────────────────────────────────┐ │
│  │  datos.gov.co          │      │  datosabiertos.bogota.gov.co     │ │
│  │  ├─ /api/3/package_search  │  │  ├─ /api/3/package_search      │ │
│  │  ├─ /api/3/action/...  │      │  ├─ /api/3/action/...          │ │
│  │  └─ 8700+ datasets     │      │  └─ 2100+ datasets             │ │
│  └────────────────────────┘      └──────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de Datos

### 1. Usuario Selecciona Territorio (Frontend)
```
Usuario selecciona Departamento + Municipio
    ↓
DashboardPage estado actualizado
    ↓
TerritorialDataCard montado con props
    ↓
useEffect dispara getTerritorialData()
```

### 2. Frontend Solicita Datos
```
externalDataService.getMunicipalityIndicators(dept, mun)
    ↓
HTTP GET /api/v1/external/municipality-indicators
    ↓
Con parámetros: ?department=X&municipality=Y
```

### 3. Backend Procesa Solicitud
```
FastAPI endpoint recibe solicitud
    ↓
external_data_service.get_municipality_indicators()
    ↓
Crea 4 tasks paralelas (población, ingreso, educación, competencia)
    ↓
asyncio.gather(*tasks) - Ejecuta en paralelo
```

### 4. Backend Consulta CKAN APIs
```
Para cada variable:
  ├─ search_territorial_data(dept, mun, "population")
  │   ├─ async client.get(datos.gov.co/api/3/package_search)
  │   ├─ async client.get(bogota.gov.co/api/3/package_search)
  │   └─ await asyncio.gather(task1, task2) - Paralelo
  │
  ├─ Procesa resultados (primeros 5 datasets)
  ├─ Extrae campos relevantes
  └─ Retorna datos procesados

Total: 8 requests HTTP paralelos (2 fuentes × 4 variables)
```

### 5. Backend Retorna Datos al Frontend
```
Estructura JSON con:
  ├─ population: { found, sources: { datos_gov, bogota } }
  ├─ income: { found, sources: { datos_gov, bogota } }
  ├─ education: { found, sources: { datos_gov, bogota } }
  └─ competition: { found, sources: { datos_gov, bogota } }
```

### 6. Frontend Renderiza Tarjeta
```
Componente monta con datos
    ↓
Usuario ve variables en botones
    ↓
Haz clic para cambiar entre variables
    ↓
Muestra datasets de ambas fuentes
```

---

## ⚡ Optimizaciones Implementadas

### 1. Concurrencia Asincrónica
```python
# En lugar de secuencial:
result1 = await search_datasets("datos_gov")
result2 = await search_datasets("bogota")
# Total: 2T

# Implementado en paralelo:
results = await asyncio.gather(
    search_datasets("datos_gov"),
    search_datasets("bogota")
)
# Total: T (más rápido)
```

### 2. Timeout de Conexión
```python
timeout = httpx.Timeout(15.0)  # Máximo 15s por request
```

### 3. Limitación de Datos
```python
# Solo retorna primeros 5 datasets por fuente
# Solo retorna primeros 3 recursos por dataset
# Solo retorna primeros 1000 filas si es CSV
```

### 4. Caché Frontend
```typescript
// Los datos se cachean en el estado React
// No se refetch a menos que cambien department/municipality
```

---

## 🔧 Configuración de CKAN

### URLs de APIs
```
DATOS GOV:
- Base: https://www.datos.gov.co/api/3
- Search: /package_search?q=...&rows=...

BOGOTÁ:
- Base: https://datosabiertos.bogota.gov.co/api/3
- Search: /package_search?q=...&rows=...
```

### Parámetros Soportados
```
q=<query>           # Búsqueda de texto
rows=<número>       # Número de resultados (máx 200)
offset=<número>     # Paginación
type=<tipo>         # Tipo de dataset (dataset, resource, etc)
sort=<campo>        # Ordenar por campo
```

### Respuesta Típica
```json
{
  "success": true,
  "result": {
    "count": 2456,
    "results": [
      {
        "id": "...",
        "name": "...",
        "title": "...",
        "notes": "...",
        "organization": { "name": "..." },
        "resources": [
          {
            "id": "...",
            "name": "...",
            "format": "CSV|JSON|...",
            "url": "https://..."
          }
        ]
      }
    ]
  }
}
```

---

## 🎯 Mappeo de Variables a Keywords CKAN

```python
{
    "population": [
        "población", "population", "habitantes", "demográfico"
    ],
    "income": [
        "ingreso", "ingresos", "income", "salario", 
        "remuneración", "económico"
    ],
    "education": [
        "educación", "education", "escolaridad", 
        "analfabetismo", "cobertura educativa"
    ],
    "competition": [
        "competencia", "competition", "empresas", 
        "actividad económica", "competitiva"
    ]
}
```

---

## 📊 Métricas y Monitoreo

### Timeouts Implementados
```python
# Conexión: 15 segundos
# Timeout total por endpoint: 20 segundos (3 variables en paralelo)
# Timeout para 4 variables en paralelo: ~25-30 segundos máximo
```

### Logging
```python
logger = logging.getLogger(__name__)

# Se registra:
- Errores de conexión
- Datasets encontrados
- Búsquedas exitosas
- Fallos de parsing
```

### Health Check
```bash
GET /api/v1/external/health

Retorna:
{
  "status": "healthy|degraded|unhealthy",
  "services": {
    "datos_gov": "available|unavailable",
    "bogota": "available|unavailable"
  }
}
```

---

## 🔐 Consideraciones de Seguridad

### 1. Validación de Entrada
```python
# Valida que department y municipality sean strings válidos
# Limita queries a caracteres seguros
```

### 2. Rate Limiting
```python
# CKAN típicamente permite 10+ req/segundo
# Implementar rate limiting adicional si es necesario
```

### 3. CORS
```python
# Validar origen en producción
# Configurar headers CORS apropiados
```

### 4. Error Handling
```python
# No expone detalles internos de errores
# Retorna mensajes genéricos al cliente
```

---

## 🚀 Próximas Mejoras

### Corto Plazo
- [ ] Implementar Redis para caché
- [ ] Agregar paginación a búsquedas
- [ ] Descargar datos en CSV/JSON/GeoJSON

### Mediano Plazo
- [ ] Integrar más fuentes de datos
- [ ] Gráficos interactivos
- [ ] Series de tiempo
- [ ] Predicciones ML

### Largo Plazo
- [ ] Data lake centralizado
- [ ] Sincronización incremental
- [ ] API pública para developers
- [ ] Integración con BI tools

---

## 📚 Referencias

- [CKAN API Documentation](http://docs.ckan.org/en/2.10/api/)
- [datos.gov.co API](https://www.datos.gov.co/)
- [Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/)
- [HTTPX Documentation](https://www.python-httpx.org/)
- [FastAPI Async](https://fastapi.tiangolo.com/async-concurrency-and-async-await/)

---

**Versión:** 1.0.0  
**Fecha:** Mayo 2026
