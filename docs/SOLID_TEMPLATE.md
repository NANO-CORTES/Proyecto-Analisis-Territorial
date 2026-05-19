# Plantilla SOLID para microservicios FastAPI

Este documento describe la arquitectura limpia (ports & adapters) que se
aplico en `Backend/analytics` y `Backend/recommendations`, y como replicarla
en el resto de servicios para cumplir con todas las HU del documento maestro.

## Capas

```
app/
  api/routers/        # Adaptadores FastAPI (HTTP -> casos de uso)
  application/
    dto.py            # Pydantic DTOs (entrada / salida)
    use_cases/        # Orquestacion de la logica de negocio
  core/
    config.py         # Settings (pydantic-settings)
    database.py       # SessionLocal y get_db
  domain/
    entities.py       # Dataclasses puros del dominio
    value_objects.py  # Enums y VOs inmutables
    ports/            # Interfaces (ABC) que el dominio necesita
    services/         # Servicios puros sin IO (calculadores, builders)
  infrastructure/
    persistence/      # Adapters de BD (SQLAlchemy)
    http/             # Adapters HTTP a otros servicios
    di.py             # Composition root (FastAPI Depends)
  main.py             # Solo instancia FastAPI + routers
```

## Como aplican los principios SOLID

- **S**RP: cada modulo tiene una unica responsabilidad. Routers solo traducen HTTP; use cases orquestan; el dominio calcula; adapters acceden a IO.
- **O**CP: para soportar otra fuente de datos (Mongo, archivo plano, mock) se anade una nueva implementacion de la interfaz en `infrastructure/` sin tocar `domain/`.
- **L**SP: cada adapter de `infrastructure/` cumple la firma exacta del puerto que implementa (`IIndicatorRepository`, `IConfigurationProvider`, ...).
- **I**SP: los puertos son granulares (`IConfigurationProvider` solo expone `get_active_weights` y `get_combined_weights`, no mezcla con auditoria).
- **D**IP: los use cases dependen siempre de interfaces (`app.domain.ports`), nunca de clases concretas. La composicion ocurre en `infrastructure/di.py` usando `Depends`.

## Checklist para refactorizar un servicio existente

1. Crear las carpetas `domain/`, `application/`, `infrastructure/` y `api/routers/` con sus `__init__.py`.
2. Mover los `Column`/`__tablename__` actuales a `infrastructure/persistence/models.py` y definir un `Base` propio.
3. Definir entidades puras (dataclasses) en `domain/entities.py` con `to_*`/`as_dict` cuando se necesite serializar.
4. Extraer la logica de negocio actual (calculos, validaciones, reglas) a `domain/services/<nombre>.py` sin imports de FastAPI/SQLAlchemy/httpx.
5. Convertir clientes httpx y queries SQL en `infrastructure/http/<cliente>.py` e `infrastructure/persistence/<repo>.py` implementando interfaces de `domain/ports/`.
6. Crear casos de uso en `application/use_cases/` que reciban los puertos por constructor y devuelvan DTOs Pydantic.
7. Mover los endpoints a `api/routers/<recurso>.py`, recibiendo el caso de uso con `Depends(get_xxx_use_case)` del nuevo `infrastructure/di.py`.
8. Sustituir el `main.py` para importar solo desde `app.api.routers` y `app.core`.
9. Eliminar los archivos antiguos (`models/`, `repositories/`, `services/`, `interfaces/`, `schemas/`, `endpoints/`) una vez los routers nuevos esten activos.
10. Volver a correr `python -m py_compile` y los tests.

## Convenciones adicionales

- No hay comentarios inline en el codigo (`#`, `//`, `/* */`). El nombre de cada clase/funcion debe ser auto-explicativo.
- Se conserva una docstring breve solo en metodos publicos cuando el dominio es ambiguo.
- Los DTOs siempre son Pydantic. Las entidades nunca son Pydantic — son dataclasses puras.
- `get_db` se inyecta desde `app.core.database`. Los adapters reciben `Session` por constructor.
- Los handlers devuelven HTTP `422` para `ValueError` (datos invalidos) y `502` para `RuntimeError` (fallo en dependencia externa).
- Los servicios externos se aislan tras puertos. Para tests se inyectan dobles en `application/use_cases/`.

## Estado actual de cumplimiento

| Servicio            | Estado refactor       | HU principales cubiertas |
|---------------------|-----------------------|--------------------------|
| ms-analytics        | Completo (plantilla)  | HU-13, HU-15, HU-16, HU-24 |
| ms-recommendations  | Completo (nuevo)      | HU-25 |
| ms-ingestion        | Pendiente             | HU-01, HU-02, HU-03, HU-04 |
| ms-transformation   | Pendiente             | HU-07, HU-20 |
| ms-configuration    | Pendiente             | HU-14 |
| ms-audit-trace      | Pendiente             | HU-09, HU-19, HU-29 |
| ms-auth             | Pendiente             | HU-10, HU-11, HU-12 |
| ms-ml               | Pendiente             | HU-22, HU-23 |
| bff-gateway         | Pendiente             | HU-17, HU-21, HU-26, HU-28 |
| frontend-web        | Faltan vistas         | HU-05, HU-18, HU-26, HU-27, HU-28, HU-29 |

Las HU "Pendiente" siguen el mismo procedimiento descrito en el checklist
y la plantilla de referencia es `Backend/analytics/app/`.
