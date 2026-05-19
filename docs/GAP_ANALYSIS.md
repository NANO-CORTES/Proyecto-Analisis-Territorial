# Gap analysis HU vs implementacion (estado actual)

## Resumen ejecutivo

| Bloque | Estado |
|---|---|
| Backend - arquitectura SOLID | ms-analytics, ms-recommendations, ms-ml refactorizados completos |
| Backend - microservicio faltante | ms-recommendations construido desde cero |
| Backend - IA funcional | ms-ml con /predict, modelo activo con joblib, train, list, activate |
| BFF gateway | endpoints consolidados /zone-summary, /compare, /dashboard-summary, /export/ranking, /export/zone-report |
| Transformacion avanzada | /transform/advanced con minmax/zscore + reporte estadistico |
| Auditoria completa | /events, /audit/user/{id}/activity, /audit/report CSV |
| Frontend | paginas ZoneComparator, Configuration, AuditTimeline, rutas registradas |
| Tests dominio | 13 tests pasando (scoring + recommendation_builder + ml_trainer) |
| Limpieza | comentarios eliminados en 120 archivos Python y 31 JS/TS |

## Sprint 1 - Gestion de datos, infraestructura y autenticacion

| HU | Estado | Notas |
|----|--------|-------|
| HU-01 Carga de dataset | Funcional | ms-ingestion expone POST /api/v1/datasets/upload |
| HU-02 Validacion | Funcional | validacion estructural con Pandas |
| HU-03 Persistencia | Funcional | dataset_load + dataset_file_reference |
| HU-04 Consulta zonas | Funcional | GET /api/v1/zones con paginacion |
| HU-05 Interfaz base | Funcional | Login, Dashboard, Analysis, Profile, UserManagement, Register, ML, Compare, Config, Audit |
| HU-06 Docker | Funcional | docker-compose levanta los 10 servicios |
| HU-07 Transformacion | Funcional | /transform basico + /transform/advanced |
| HU-08 Health checks | Funcional | /health en todos los servicios |
| HU-09 Auditoria basica | Funcional | /audit/trace + /events |
| HU-10 Autenticacion JWT | Funcional | login, register, me, logout en ms-auth |
| HU-11 Roles | Funcional | ADMIN/USER + ProtectedRoute |
| HU-12 Gestion de usuarios | Funcional | endpoints admin + UI |

## Sprint 2 - Analitica, scoring, visualizacion y orquestacion

| HU | Estado | Notas |
|----|--------|-------|
| HU-13 Indicadores | Funcional | CalculateIndicatorsUseCase + persistencia |
| HU-14 Configuracion | Funcional | endpoints en ms-configuration + UI ConfigurationPage |
| HU-15 Scoring | Funcional | ExecuteScoringUseCase con formula ponderada y penalizacion |
| HU-16 Ranking | Funcional | GetRankingUseCase con paginacion y filtros |
| HU-17 BFF | Funcional | /api/bff/zone-summary consolidado |
| HU-18 Visualizacion | Funcional | AnalysisPage + Recharts |
| HU-19 Trazabilidad analitica | Funcional | eventos INDICATORS_CALCULATED, SCORING_EXECUTED |
| HU-20 Normalizacion avanzada | Funcional | /transform/advanced con minmax/zscore + winsorizacion p99 + reporte |
| HU-21 Comparacion de zonas | Funcional | /api/bff/compare + pagina ZoneComparator (radar + sintesis) |

## Sprint 3 - Inteligencia, prediccion, recomendaciones y cierre

| HU | Estado | Notas |
|----|--------|-------|
| HU-22 Modelo ML | Funcional | TrainModelUseCase con sklearn (linear/random_forest/gradient_boosting) + joblib + metricas |
| HU-23 Prediccion | Funcional | POST /api/v1/ml/predict con modelo activo + Alto/Medio/Bajo + confidence_score |
| HU-24 Integracion IA | Funcional | ExecuteCombinedScoringUseCase con flag de discrepancia |
| HU-25 Recomendaciones | Funcional | ms-recommendations completo (fortalezas, riesgos, explicacion) |
| HU-26 Dashboard | Funcional | /api/bff/dashboard-summary + DashboardPage |
| HU-27 Comparacion avanzada | Funcional | pestaña Vista IA en ZoneComparator + sintesis automatica |
| HU-28 Exportacion | Funcional | /api/bff/export/ranking (CSV) + /api/bff/export/zone-report (JSON) |
| HU-29 Auditoria completa | Funcional | /events, /audit/user/{id}/activity, /audit/report CSV + AuditTimelinePage |
| HU-30 Integracion final | Pendiente | requiere ejecucion docker-compose con dataset real |

## Como ejecutar el sistema completo

1. `docker compose up --build` desde la raiz del proyecto.
2. Esperar a que los 10 servicios respondan `/health` con HTTP 200.
3. Acceder a `http://localhost:5173`, registrar un usuario, iniciar sesion.
4. Subir un dataset CSV con columnas zone_code, zone_name + variables numericas.
5. Validar -> transformar -> calcular indicadores -> ejecutar scoring -> entrenar modelo ML -> activarlo -> generar recomendaciones -> ver dashboard.
6. Comparar zonas en `/compare`, ajustar pesos en `/configuration`, ver auditoria en `/audit`.

## Servicios y puertos (segun flujo de ejecucion)

| # | Servicio | Puerto | Rol |
|---|---|---|---|
|  | db-postgres | 5432 | Persistencia |
|  | frontend-web | 5173 | UI |
| 1 | bff-gateway | 8001 | Puerta de entrada |
| 2 | ms-auth | 8002 | Autenticacion / roles |
| 3 | ms-ingestion | 8003 | Carga de datasets |
| 4 | ms-transformation | 8004 | Limpieza y normalizacion |
| 5 | ms-configuration | 8005 | Pesos y parametros |
| 6 | ms-analytics | 8006 | Indicadores, scoring, ranking |
| 7 | ms-audit-trace | 8007 | Auditoria y trazabilidad |
| 8 | ms-ml | 8008 | Machine learning + /predict |
| 9 | ms-recommendations | 8009 | Recomendaciones explicadas |

El frontend consume al BFF en `http://localhost:8001`. Cada servicio se direcciona dentro de la red Docker por su nombre (`http://ms-auth:8002`, etc.).
