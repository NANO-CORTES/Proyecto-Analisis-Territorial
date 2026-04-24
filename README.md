# Proyecto de Análisis Territorial

Este proyecto es una plataforma de microservicios diseñada para el análisis de datos territoriales, integrando recolección de datos (ingesta), transformación, analítica y visualización.

## 🏛 Arquitectura del Sistema

La solución utiliza una arquitectura de microservicios coordinada mediante Docker Compose y un patrón **BFF (Backend for Frontend)** a través de un Gateway:

- **Frontend (Port 5173)**: Aplicación React (Vite) para la interacción del usuario.
- **BFF Gateway (Port 8000)**: Punto único de entrada que orquesta las peticiones a los microservicios.
- **MS Ingestion (Port 8001)**: Carga y validación de archivos CSV/JSON.
- **MS Auth (Port 8006)**: Gestión de usuarios, roles y seguridad JWT.
- **MS Audit Trace (Port 8002)**: Registro de auditoría de todas las acciones del sistema.
- **MS Configuration (Port 8003)**: Gestión de parámetros del sistema.
- **MS Transformation (Port 8004)**: Procesamiento y limpieza de datos territoriales.
- **MS Analytics (Port 8005)**: Generación de insights y analítica descriptiva.

---

## 📜 Convenciones del Proyecto (IMPORTANTE)

Para mantener la consistencia del código entre compañeros, se han establecido las siguientes reglas:

1.  **Estilo de Nombrado**: Usar `camelCase` para nombres de variables, funciones y parámetros (ej. `processUpload`, `userId`).
2.  **Principios SOLID**: Cada clase y módulo debe tener una responsabilidad única. Las dependencias deben inyectarse (Dependency Inversion).
3.  **Modelos de Datos**: Las clases de SQLAlchemy mapean snake_case en la BD a atributos camelCase en Python para facilitar la integración con el frontend.

---

## 🚀 Cambios Recientes y Ajustes Técnicos

Se han realizado los siguientes ajustes críticos para mejorar la robustez del sistema:

### Servicio de Ingesta
- **Metadatos Expandidos**: Ahora es posible enviar `sourceName` y `sourceType` al cargar un dataset.
- **Soporte Territorial**: Se integró el campo `department` en la extracción de zonas para mejorar el filtrado geográfico.

### Servicio de Autenticación
- **Bypass del Límite de Bcrypt (72 bytes)**: Se implementó un *pre-hashing* con SHA256 antes de Bcrypt. Esto permite contraseñas de cualquier longitud sin causar errores de `ValueError` en el servidor.
- **Refactorización Global**: Todos los endpoints de Auth y Users han sido actualizados a `camelCase`.

---

## 🛠 Instalación y Ejecución

1.  Asegúrate de tener Docker y Docker Compose instalados.
2.  Crea un archivo `.env` basado en el entorno de desarrollo (ver variables en `docker-compose.yml`).
3.  Ejecuta el comando:
    ```bash
    docker-compose up --build
    ```
4.  Accede a la documentación Interactiva (Swagger):
    *   Ingesta: `http://localhost:8001/docs`
    *   Auth: `http://localhost:8006/docs`
    *   Gateway (Proxy): `http://localhost:8000/docs`

---

## 🧪 Verificación

Para validar que los cambios en la lógica de ingesta funcionan correctamente sin necesidad de levantar toda la infraestructura de base de datos, puedes ejecutar el script de prueba:

```bash
cd Backend/ingestion
python verify_changes.py
```

---
*Mantenido por el equipo de Ingeniería de Software - Proyecto Análisis Territorial.*