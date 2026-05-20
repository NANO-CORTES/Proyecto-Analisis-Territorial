# Datasets de demostración

Datasets listos para cargar en la plataforma durante la exposición o demo.

## Archivos disponibles

| Archivo | Formato | Zonas | Origen sintético basado en |
|---------|---------|-------|----------------------------|
| `bogota_demo_dataset.json` | JSON | 20 localidades de Bogotá | DANE 2024 (aprox.) |
| `medellin_demo_dataset.csv` | CSV | 20 comunas de Medellín | DANE 2024 (aprox.) |

## Variables incluidas

Cada zona contiene:

- `zone_code` (str) — identificador único territorial.
- `zone_name` (str) — nombre de la zona.
- `population_density` (int) — habitantes por km².
- `average_income` (int) — ingreso promedio en COP.
- `education_level` (int 0-100) — índice educativo.
- `economic_activity_index` (int 0-100) — actividad económica.
- `commercial_presence_index` (int 0-100) — presencia comercial.

Estas variables se mapean automáticamente a los cuatro indicadores del modelo:
Población, Ingresos, Educación y Competitividad (penalización).

## Flujo de demostración recomendado

1. Iniciar sesión con `admin@territorial.com`.
2. En el Dashboard, clic en el botón flotante de carga y subir `bogota_demo_dataset.json`.
3. Ir a Análisis → seleccionar el dataset recién cargado y ejecutar los 5 pasos.
4. Ir a Experimentos ML → entrenar un modelo (Random Forest sugerido).
5. Activar el modelo entrenado.
6. Volver al Dashboard → Reportes → descargar el último análisis en CSV, JSON o XLS.

Cada dataset produce un ranking distinto. Para mostrar la variabilidad del modelo,
sube primero el CSV de Medellín y compáralo con el JSON de Bogotá.
