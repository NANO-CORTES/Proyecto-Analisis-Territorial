# Integración de Datos Externos - Guía de Uso

## 📊 Descripción General

La plataforma ahora está integrada con los portales de datos abiertos:
- **datos.gov.co** - Portal Nacional de Datos Abiertos de Colombia
- **datosabiertos.bogota.gov.co** - Portal de Datos Abiertos de Bogotá

Esto permite cargar automáticamente datos sobre **población**, **ingresos**, **educación** y **competencia** para cualquier departamento y municipio de Colombia.

---

## 🎯 Variables Soportadas

La plataforma carga datos de 4 variables territoriales:

### 1. **Población** 👥
- Datos demográficos
- Densidad poblacional
- Proyecciones de crecimiento
- **Fuentes:** DANE, Ministerio del Interior, datos.gov.co

### 2. **Ingreso** 💰
- Salarios promedio
- Ingresos per cápita
- Indicadores económicos
- **Fuentes:** DANE, Ministerio de Hacienda, datos.gov.co

### 3. **Educación** 🎓
- Cobertura educativa
- Índices de escolaridad
- Analfabetismo
- **Fuentes:** Ministerio de Educación, ICFES, datos.gov.co

### 4. **Competencia** 📊
- Actividad económica
- Sectores empresariales
- Competitividad territorial
- **Fuentes:** Superintendencia de Sociedades, Cámara de Comercio, datos.gov.co

---

## 🚀 Cómo Usar

### Paso 1: Acceder al Dashboard
1. Inicia sesión en la plataforma
2. Ve a **Dashboard** desde el menú principal

### Paso 2: Seleccionar Territorio
1. En la sección "Territorios", selecciona un **Departamento**
2. Se mostrarán los **Municipios** disponibles
3. Selecciona uno o más municipios

### Paso 3: Ver Datos Integrados
Una vez seleccionado un municipio, aparecerá una tarjeta con:

```
┌─ Datos Territoriales ─────────────────────┐
│ Departamento - Municipio                  │
├──────────────────────────────────────────┤
│ [👥 Población] [💰 Ingreso]              │
│ [🎓 Educación] [📊 Competencia]          │
├──────────────────────────────────────────┤
│ Datasets encontrados:                    │
│                                          │
│ 📊 Datos.gov.co                          │
│  - Dataset 1                             │
│  - Dataset 2                             │
│                                          │
│ 🏛️ Datos Abiertos Bogotá                 │
│  - Dataset 3                             │
│  - Dataset 4                             │
└──────────────────────────────────────────┘
```

### Paso 4: Cambiar entre Variables
Haz clic en los botones de variables para ver diferentes datasets:
- **Población** → Datos demográficos
- **Ingreso** → Datos económicos
- **Educación** → Datos educativos
- **Competencia** → Datos de actividad económica

---

## 🔌 Endpoints Backend

### Obtener Datos Territoriales por Variable

```bash
GET /api/v1/external/territorial-data
```

**Parámetros:**
- `department` (string, requerido): Departamento
- `municipality` (string, requerido): Municipio
- `variable` (string, opcional): `population`, `income`, `education`, `competition`

**Ejemplo:**
```bash
GET /api/v1/external/territorial-data?department=Bogota&municipality=Chapinero&variable=population
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "variable": "population",
    "department": "Bogota",
    "municipality": "Chapinero",
    "sources": {
      "datos_gov": [
        {
          "id": "dataset-123",
          "name": "Población por municipio",
          "title": "Datos de población DANE",
          "organization": "DANE",
          "resources": [...]
        }
      ],
      "bogota": [...]
    },
    "found": true
  }
}
```

### Obtener Todos los Indicadores

```bash
GET /api/v1/external/municipality-indicators
```

**Parámetros:**
- `department` (string, requerido)
- `municipality` (string, requerido)

**Respuesta:** Retorna los 4 indicadores (población, ingreso, educación, competencia) en paralelo

### Buscar Datasets

```bash
GET /api/v1/external/search-datasets
```

**Parámetros:**
- `query` (string, requerido): Término de búsqueda
- `organization` (string, opcional): `datos_gov` o `bogota`

### Query Directa CKAN

```bash
GET /api/v1/external/ckan-query
```

Para queries personalizadas a las APIs CKAN

---

## 🛠️ Arquitectura Técnica

### Backend (Python/FastAPI)

#### Servicio: `external_data_service.py`
```python
# Buscar datos territoriales
await external_data_service.search_territorial_data(
    department="Bogota",
    municipality="Chapinero",
    variable="population"
)

# Obtener todos los indicadores
await external_data_service.get_municipality_indicators(
    department="Bogota",
    municipality="Chapinero"
)
```

#### Endpoints: `external_data.py`
- `/api/v1/external/territorial-data` - GET datos específicos
- `/api/v1/external/municipality-indicators` - GET todos indicadores
- `/api/v1/external/search-datasets` - GET búsqueda de datasets
- `/api/v1/external/ckan-query` - GET query personalizada
- `/api/v1/external/health` - GET estado del servicio

### Frontend (React/TypeScript)

#### Servicio: `externalDataApi.ts`
```typescript
// Importar servicio
import { externalDataService } from '../services/externalDataApi';

// Obtener datos
const result = await externalDataService.getTerritorialData(
  'Bogota',
  'Chapinero',
  'population'
);

// Obtener todos indicadores
const indicators = await externalDataService.getMunicipalityIndicators(
  'Bogota',
  'Chapinero'
);
```

#### Componente: `TerritorialDataCard.tsx`
```tsx
import TerritorialDataCard from '../components/TerritorialDataCard';

<TerritorialDataCard 
  department="Bogota" 
  municipality="Chapinero" 
/>
```

---

## ⚙️ Instalación y Configuración

### 1. Instalar Dependencias Backend

```bash
cd Backend/ingestion
pip install httpx  # Para peticiones HTTP async
pip install pandas  # Para procesamiento de datos
```

### 2. Variables de Entorno

Agregar al `.env` (si es necesario):
```bash
# Las URLs de CKAN están hardcodeadas en external_data_service.py
# Pero puedes personalizarlas según necesites
```

### 3. Iniciar Backend

```bash
cd Backend/ingestion
python -m uvicorn app.main:app --reload --port 8001
```

### 4. Verificar Integración

```bash
curl "http://localhost:8001/api/v1/external/health"
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

---

## 📈 Casos de Uso

### 1. Análisis Comparativo
Selecciona múltiples municipios para comparar sus indicadores territoriales.

### 2. Investigación Territorial
Accede a datasets detallados sobre cualquier territorio de Colombia.

### 3. Toma de Decisiones
Usa los datos para decisiones de inversión, planificación o política pública.

### 4. Integración de Datos
Combina datos de múltiples fuentes en un único análisis territorial.

---

## 🔍 Búsqueda Avanzada

### Filtrar por Variable Específica
```
GET /api/v1/external/territorial-data?department=Antioquia&municipality=Medellín&variable=income
```

### Búsqueda Full-Text
```
GET /api/v1/external/search-datasets?query=salario+promedio&organization=datos_gov
```

### Query CKAN Personalizada
```
GET /api/v1/external/ckan-query?query=población+2024&organization=bogota
```

---

## ⚡ Rendimiento

- **Timeout de conexión:** 15 segundos por request
- **Límite de datasets:** 5 por fuente
- **Caché:** Los datos se buscan en tiempo real (considera implementar caché Redis)
- **Rate limiting:** Respeta los límites de CKAN (10+ req/segundo típicamente)

---

## 🐛 Troubleshooting

### Error: "No se encontraron datos"
- Verifica que el nombre del departamento/municipio sea correcto
- Intenta con diferentes variables
- Comprueba la conexión a internet

### Error: "Error al conectar con los datos externos"
- Verifica que los portales de datos estén en línea:
  - https://datos.gov.co/api/3/package_search
  - https://datosabiertos.bogota.gov.co/api/3/package_search
- Revisa el log del backend para más detalles

### Datos lentos
- Los primeros requests pueden tardar más (búsqueda en CKAN)
- Los datos se cachean en el componente React
- Considera implementar Redis en producción

---

## 📋 Próximas Mejoras

- [ ] Implementar caché de datos (Redis)
- [ ] Añadir más variables territoriales
- [ ] Integrar datos geoespaciales
- [ ] Descargar datos en múltiples formatos (CSV, GeoJSON)
- [ ] Gráficos interactivos de series de tiempo
- [ ] Alertas de nuevos datasets
- [ ] API para developers externos

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la documentación de CKAN: http://docs.ckan.org/
2. Contacta con los portales de datos
3. Abre un issue en el repositorio del proyecto

---

**Última actualización:** Mayo 2026
**Versión:** 1.0.0
