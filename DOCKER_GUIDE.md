# 🐳 Dockerización - Plataforma de Análisis Territorial

Guía completa para ejecutar la plataforma completa en Docker.

---

## 📋 Requisitos Previos

### Instalación de Docker

#### Windows
1. Descarga **Docker Desktop for Windows** desde: https://www.docker.com/products/docker-desktop
2. Ejecuta el instalador
3. Reinicia tu computadora
4. Abre PowerShell y verifica:
```bash
docker --version
docker-compose --version
```

#### Mac
1. Descarga **Docker Desktop for Mac** desde: https://www.docker.com/products/docker-desktop
2. Ejecuta el instalador
3. Verifica en Terminal:
```bash
docker --version
docker-compose --version
```

#### Linux (Ubuntu/Debian)
```bash
# Instalar Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Agregar tu usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Verificar
docker --version
docker-compose --version
```

---

## 🚀 Inicio Rápido (5 minutos)

### 1. Clonar Repositorio
```bash
cd ~/tu-directorio
git clone <tu-repo>
cd Proyecto-Analisis-Territorial
```

### 2. Crear Archivo .env
```bash
# Copiar del ejemplo
cp .env.example .env

# Editar (opcional: cambiar contraseña de BD)
# Variables importantes:
# - POSTGRES_PASSWORD=admin
# - VITE_API_BASE_URL=http://localhost:8001
```

### 3. Levantar Plataforma Completa
```bash
# Construir imágenes y levantar servicios
docker-compose up -d

# O con rebuild de imágenes
docker-compose up -d --build
```

### 4. Verificar Estado
```bash
# Ver servicios en ejecución
docker-compose ps

# Esperado: Todos con status "Up"
CONTAINER ID  IMAGE                          STATUS
abc123        proyecto-ms-ingestion:latest   Up 2 minutes
def456        proyecto-bff-gateway:latest    Up 2 minutes
ghi789        postgres:15-alpine             Up 2 minutes
...
```

### 5. Acceder a Plataforma
- **Frontend:** http://localhost:5173
- **API Gateway:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs

### 6. Detener Plataforma
```bash
# Detener todos los servicios
docker-compose down

# Detener y eliminar datos (cuidado)
docker-compose down -v
```

---

## 🔧 Comandos Comunes

### Ver Logs
```bash
# Logs de todos los servicios
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs -f ms-ingestion
docker-compose logs -f bff-gateway
docker-compose logs -f frontend-web

# Últimas 100 líneas
docker-compose logs --tail=100 ms-ingestion
```

### Ejecutar Comandos en Contenedor
```bash
# Conectar a bash del ingestion service
docker-compose exec ms-ingestion bash

# Ejecutar comando específico
docker-compose exec ms-ingestion python -c "import sys; print(sys.version)"

# Acceder a PostgreSQL
docker-compose exec db-postgres psql -U postgres -d territorial_db
```

### Reconstruir Servicios
```bash
# Reconstruir todas las imágenes
docker-compose build

# Reconstruir servicio específico
docker-compose build ms-ingestion

# Reconstruir sin caché
docker-compose build --no-cache
```

### Reiniciar Servicios
```bash
# Reiniciar todos
docker-compose restart

# Reiniciar específico
docker-compose restart ms-ingestion

# Parar un servicio
docker-compose stop ms-ingestion

# Iniciar un servicio detenido
docker-compose start ms-ingestion
```

---

## 📊 Arquitectura de Servicios

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Node.js)                       │
│  Puerto: 5173  |  http://localhost:5173                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│         BFF GATEWAY (FastAPI/Python)                        │
│  Puerto: 8001  |  http://localhost:8001                   │
│  Docs: http://localhost:8001/docs                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ Ingestion│  │   Auth   │  │ Transformation
│ Puerto   │  │ Puerto   │  │ Puerto 8004  │
│ 8003     │  │ 8002     │  └──────────────┘
└──────────┘  └──────────┘
              
      ┌───────────────┬───────────────┐
      │               │               │
      ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│Analytics │  │ Config   │  │ Audit Trace  │
│Puerto    │  │ Puerto   │  │ Puerto 8007  │
│8006      │  │ 8005     │  └──────────────┘
└──────────┘  └──────────┘

      ┌───────────────┬───────────────┐
      │               │               │
      ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│    ML    │  │Recommend-│  │  Database    │
│ Puerto   │  │ations    │  │ PostgreSQL   │
│ 8008     │  │ Puerto   │  │ Puerto 5432  │
│          │  │ 8009     │  └──────────────┘
└──────────┘  └──────────┘

              
              ┌──────────┐
              │ Volumes  │
              │Compartid┤
              │os        │
              └──────────┘
```

---

## 🗄️ Gestión de Base de Datos

### Conectar a PostgreSQL
```bash
# Acceder al contenedor PostgreSQL
docker-compose exec db-postgres psql -U postgres -d territorial_db

# Dentro de psql:
# Ver bases de datos
\l

# Conectar a base de datos
\c territorial_db

# Ver tablas
\dt

# Ver esquemas
\dn
```

### Backup de Base de Datos
```bash
# Crear backup
docker-compose exec db-postgres pg_dump -U postgres territorial_db > backup.sql

# Restaurar desde backup
docker-compose exec -T db-postgres psql -U postgres territorial_db < backup.sql
```

### Limpiar Base de Datos
```bash
# Eliminar todos los datos (pero mantener estructura)
docker-compose exec db-postgres psql -U postgres -d territorial_db -c "TRUNCATE TABLE ingestion.dataset_loads CASCADE;"

# Eliminar todo incluyendo volumen
docker-compose down -v
```

---

## 🔐 Variables de Entorno

### Archivo .env Explicado

```bash
# Base de Datos
POSTGRES_USER=postgres                    # Usuario PostgreSQL
POSTGRES_PASSWORD=admin                   # Contraseña (cambiar en prod)
POSTGRES_DB=territorial_db                # Nombre de BD
DATABASE_URL=postgresql://...             # URL de conexión

# Autenticación
SECRET_KEY=tu-clave-secreta              # Para JWT tokens (cambiar en prod)
ALGORITHM=HS256                           # Algoritmo de firmado

# APIs Externas
VITE_API_BASE_URL=http://localhost:8001  # URL del Gateway (como ve el cliente)

# Ambiente
ENVIRONMENT=development                   # development|staging|production
DEBUG=true                                # Mostrar debug logs
```

### En Producción
```bash
# NUNCA hagas esto:
❌ POSTGRES_PASSWORD=admin
❌ SECRET_KEY=my-secret
❌ DEBUG=true
❌ ENVIRONMENT=development

# Haz esto:
✅ POSTGRES_PASSWORD=<generated-secure-password>
✅ SECRET_KEY=<generated-strong-secret>
✅ DEBUG=false
✅ ENVIRONMENT=production
```

---

## 🆘 Troubleshooting

### Error: "docker: command not found"
```
Solución: Docker no está instalado o no está en PATH
- Reinstala Docker Desktop
- Reinicia tu terminal/computadora
- Verifica: docker --version
```

### Error: "Cannot connect to Docker daemon"
```
Solución: Docker daemon no está ejecutándose
- Abre Docker Desktop
- En Linux: sudo systemctl start docker
- Verifica: docker ps
```

### Error: "Port already in use"
```
Solución: El puerto ya está en uso por otro servicio
Opción 1: Cambiar puerto en docker-compose.yml
  - Cambiar "8001:8001" a "8005:8001" (primer número es puerto host)
  
Opción 2: Detener el servicio que usa el puerto
  - Windows: netstat -ano | findstr :8001
  - Mac/Linux: lsof -i :8001
```

### Error: "out of memory"
```
Solución: Docker no tiene suficiente memoria
- Aumentar memoria en Docker Desktop settings
- Reducir cantidad de servicios activos
- Limpiar imágenes y contenedores no usados:
  docker system prune -a
```

### Servicio no inicia
```
Solución: Ver logs del servicio
docker-compose logs ms-ingestion

Errores comunes:
- Database connection error: Esperar a que PostgreSQL esté listo
- Import error: Reinstalar dependencias (docker-compose build --no-cache)
- Port conflict: Cambiar puerto en docker-compose.yml
```

### Frontend no puede conectar a API
```
Solución: Verificar VITE_API_BASE_URL
- En .env: VITE_API_BASE_URL=http://localhost:8001
- En producción: cambiar a URL del servidor real
- Limpiar caché del navegador (Ctrl+Shift+Delete)
```

---

## 🔒 Seguridad en Docker

### 1. No Guardes Secretos en .env
```bash
# ❌ MAL
SECRET_KEY=mi-clave-secreta
POSTGRES_PASSWORD=admin

# ✅ BIEN (usar secretos de Docker/Kubernetes)
docker secret create db_password -
docker run --secret db_password ...
```

### 2. Usa Variables en Producción
```bash
# Usar secret manager
export SECRET_KEY=$(aws secretsmanager get-secret-value ...)
export POSTGRES_PASSWORD=$(aws secretsmanager get-secret-value ...)
```

### 3. Limita Acceso a Red
```yaml
# docker-compose.yml
networks:
  plataforma-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16  # Red privada
```

### 4. Escanea Imágenes
```bash
# Usar Trivy para escanear vulnerabilidades
trivy image python:3.11-slim
trivy image proyecto-ms-ingestion:latest
```

---

## 📈 Monitoreo en Docker

### Ver Uso de Recursos
```bash
# Stats en tiempo real
docker stats

# O para contenedor específico
docker stats ms-ingestion
```

### Health Checks
```bash
# Ver estado de health checks
docker-compose ps

# Ver detalles de health check
docker inspect ms-ingestion | grep -A 5 "Health"
```

### Logs Agregados
```bash
# Ver logs de todos los servicios
docker-compose logs -f --tail=100

# Exportar logs a archivo
docker-compose logs > logs-export.txt
```

---

## 🔄 Actualización de Código

### Después de cambios en código

```bash
# Opción 1: Reconstruir servicios específicos
docker-compose build ms-ingestion
docker-compose up -d ms-ingestion

# Opción 2: Reconstruir todo
docker-compose down
docker-compose up -d --build

# Opción 3: Reload en desarrollo (hot reload)
# Los servicios con volumes:./Backend/xxx:/app usarán hot reload
# Solo espera que se recargen
```

---

## 📦 Producción con Docker

### Docker Swarm (múltiples máquinas)
```bash
# Inicializar swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml plataforma

# Ver servicios
docker service ls
```

### Kubernetes (recomendado para producción)
```bash
# Usar: Skaffold, Kustomize, o Helm
# Crear manifiestos Kubernetes:

cat > deployment.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ms-ingestion
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: ms-ingestion
        image: proyecto-ms-ingestion:latest
        ports:
        - containerPort: 8003
        env:
        - name: ENVIRONMENT
          value: production
EOF

# Deploy
kubectl apply -f deployment.yaml
```

---

## 🎯 Mejores Prácticas

### ✅ SI
- ✅ Usar `.dockerignore` para reducir tamaño
- ✅ Multi-stage builds para optimizar imágenes
- ✅ Health checks en cada servicio
- ✅ Volúmenes para datos persistentes
- ✅ Networks separadas para seguridad
- ✅ Limites de recursos (memory, cpu)

### ❌ NO
- ❌ Ejecutar como root en contenedores
- ❌ Guardar secretos en Dockerfile
- ❌ Usar `latest` tag en producción
- ❌ Logs sin rotación
- ❌ Contenedores sin health checks
- ❌ Compartir imágenes sin escaneo

---

## 📚 Recursos Adicionales

- [Docker Official Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security](https://docs.docker.com/engine/security/)

---

**Última actualización:** Mayo 2026  
**Versión:** 1.0.0
