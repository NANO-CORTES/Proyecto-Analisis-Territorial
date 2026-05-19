# ms-recommendations

Microservicio de recomendaciones (HU-25).

Genera, persiste y expone recomendaciones explicadas por zona a partir
de los resultados de scoring y predicciones del microservicio analitico y
del microservicio de machine learning.

## Endpoints

- `POST /api/v1/recommendations/generate` — recibe `score_execution_id` y opcionalmente `prediction_batch_id`. Construye fortalezas, riesgos y explicaciones por zona, las persiste y devuelve el batch generado.
- `GET /api/v1/recommendations/{zone_code}` — devuelve la recomendacion mas reciente por zona.
- `GET /health` — estado del servicio y conexion a la base de datos.

## Arquitectura

Se aplica la plantilla SOLID del proyecto (ver `docs/SOLID_TEMPLATE.md` en la raiz):

```
app/
  api/routers/        # adaptadores FastAPI
  application/        # dto + casos de uso
  core/               # config + sesion SQLAlchemy
  domain/             # entidades, puertos, servicios puros
  infrastructure/     # adapters de HTTP y persistencia + DI
  main.py             # composition root
```

## Ejecucion local

```
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8007
```

## Docker

```
docker build -t ms-recommendations .
docker run -p 8007:8007 --env-file .env ms-recommendations
```
