# 🐳 Inicio Rápido - Docker

Guía rápida para ejecutar la plataforma con Docker.

---

## 📋 Requisitos

- Docker Desktop instalado ([Descargar](https://www.docker.com/products/docker-desktop))
- docker --version
- docker-compose --version

---

## ⚡ En 3 Pasos

### 1️⃣ Preparar Entorno
```bash
# Copiar variables de entorno
cp .env.example .env

# (Opcional) Editar .env con valores personalizados
# nano .env  # o usa tu editor favorito
```

### 2️⃣ Levantar Plataforma
```bash
# Opción A: Con docker-compose directamente
docker-compose up -d --build

# Opción B: Con el script (recomendado en desarrollo)
./docker-manage.sh up          # Linux/Mac
docker-manage.bat up           # Windows

# Opción C: Con Makefile (Linux/Mac)
make up
```

### 3️⃣ Acceder
```
Frontend:  http://localhost:5173
API:       http://localhost:8001
Docs:      http://localhost:8001/docs
```

---

## 🛠️ Comandos Rápidos

### Desarrollo
```bash
# Ver logs en tiempo real
./docker-manage.sh logs                    # Todo
./docker-manage.sh logs ms-ingestion       # Servicio específico

# Conectar a contenedor
./docker-manage.sh shell ms-ingestion      # Terminal del servicio

# Reiniciar servicio
docker-compose restart ms-ingestion
```

### Base de Datos
```bash
# Conectar a PostgreSQL
./docker-manage.sh db-shell

# Crear backup
./docker-manage.sh db-backup
```

### Detener/Limpiar
```bash
# Detener servicios (mantener datos)
./docker-manage.sh down

# Limpiar todo (elimina datos)
./docker-manage.sh clean
```

---

## 📊 Servicios Disponibles

| Servicio | Puerto | URL |
|----------|--------|-----|
| Frontend | 5173 | http://localhost:5173 |
| Gateway API | 8001 | http://localhost:8001 |
| Auth | 8002 | http://localhost:8002 |
| Ingestion | 8003 | http://localhost:8003 |
| Transformation | 8004 | http://localhost:8004 |
| Configuration | 8005 | http://localhost:8005 |
| Analytics | 8006 | http://localhost:8006 |
| Audit | 8007 | http://localhost:8007 |
| ML | 8008 | http://localhost:8008 |
| Recommendations | 8009 | http://localhost:8009 |
| PostgreSQL | 5432 | localhost:5432 |

---

## 🔍 Validar Setup

```bash
# Ver estado de servicios
docker-compose ps

# Esperado: todos con STATUS "Up"
```

---

## ❓ Problemas Comunes

### "Port already in use"
```bash
# Cambiar puerto en docker-compose.yml
# Línea: ports: - "8001:8001"
# Cambiar a: ports: - "8005:8001"
```

### "Cannot connect to Docker daemon"
```bash
# Abrir Docker Desktop
# O en Linux: sudo systemctl start docker
```

### "Frontend no puede conectar a API"
```bash
# Editar .env
# VITE_API_BASE_URL=http://localhost:8001
```

---

## 📚 Documentación Completa

Para información detallada, ver [DOCKER_GUIDE.md](DOCKER_GUIDE.md)

---

## ✨ Scripts Disponibles

**Windows:** `docker-manage.bat`
```bash
docker-manage.bat up              # Levantar
docker-manage.bat logs            # Ver logs
docker-manage.bat shell ms-ingestion  # Terminal
docker-manage.bat help            # Ayuda
```

**Linux/Mac:** `docker-manage.sh` o `make`
```bash
./docker-manage.sh up             # Levantar
./docker-manage.sh logs           # Ver logs
./docker-manage.sh shell ms-ingestion  # Terminal

# O con Makefile
make up                           # Levantar
make logs                         # Ver logs
make help                         # Ayuda
```

---

## 🚀 Siguiente Paso

Ir a [DOCKER_GUIDE.md](DOCKER_GUIDE.md) para:
- Comandos avanzados
- Configuración de producción
- Troubleshooting detallado
- Mejores prácticas

---

**Última actualización:** Mayo 2026
