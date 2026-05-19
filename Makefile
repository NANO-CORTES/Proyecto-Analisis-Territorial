# Makefile para gestionar la plataforma con Docker (Linux/Mac)
# Uso: make [comando]

.PHONY: help up down restart logs status shell build clean db-backup db-shell stats

help:
	@echo "🐳 Gestor de Plataforma con Docker"
	@echo ""
	@echo "Comandos Principales:"
	@echo "  make up              Levantar todos los servicios"
	@echo "  make down            Detener todos los servicios"
	@echo "  make restart         Reiniciar todos los servicios"
	@echo "  make status          Ver estado de los servicios"
	@echo ""
	@echo "Desarrollo:"
	@echo "  make logs            Ver logs de todos los servicios"
	@echo "  make logs-ingestion  Ver logs del servicio ingestion"
	@echo "  make logs-gateway    Ver logs del gateway"
	@echo "  make logs-frontend   Ver logs del frontend"
	@echo "  make shell           Conectar a bash de un servicio"
	@echo "  make build           Construir todas las imágenes"
	@echo ""
	@echo "Base de Datos:"
	@echo "  make db-shell        Conectar a PostgreSQL"
	@echo "  make db-backup       Crear backup de base de datos"
	@echo ""
	@echo "Limpieza:"
	@echo "  make clean           Limpiar contenedores, imágenes y volúmenes"
	@echo "  make stats           Ver uso de recursos"
	@echo ""

up:
	@echo "⬆️  Levantando servicios..."
	docker-compose up -d --build
	@echo "✓ Plataforma levantada"
	@echo "Frontend: http://localhost:5173"
	@echo "API: http://localhost:8001"
	@echo "Docs: http://localhost:8001/docs"

down:
	@echo "⬇️  Deteniendo servicios..."
	docker-compose down
	@echo "✓ Servicios detenidos"

restart:
	@echo "🔄 Reiniciando servicios..."
	docker-compose restart
	@echo "✓ Servicios reiniciados"

status:
	@echo "📊 Estado de los servicios:"
	docker-compose ps

logs:
	docker-compose logs -f --tail=100

logs-ingestion:
	docker-compose logs -f --tail=100 ms-ingestion

logs-gateway:
	docker-compose logs -f --tail=100 bff-gateway

logs-frontend:
	docker-compose logs -f --tail=100 frontend-web

shell:
	@read -p "Nombre del servicio: " service; \
	docker-compose exec $$service bash

build:
	@echo "🔨 Construyendo imágenes..."
	docker-compose build
	@echo "✓ Construcción completada"

clean:
	@echo "🗑️  Limpiando..."
	docker-compose down -v
	@echo "✓ Limpieza completada"

stats:
	docker stats

db-shell:
	@echo "🐘 Conectando a PostgreSQL..."
	docker-compose exec db-postgres psql -U postgres -d territorial_db

db-backup:
	@echo "💾 Creando backup..."
	docker-compose exec -T db-postgres pg_dump -U postgres territorial_db > backup-$$(date +%Y%m%d_%H%M%S).sql
	@echo "✓ Backup creado"

env:
	@if [ ! -f .env ]; then \
		echo "📝 Creando .env desde .env.example"; \
		cp .env.example .env; \
		echo "✓ Archivo .env creado. Edítalo con tus variables"; \
	else \
		echo "✓ Archivo .env ya existe"; \
	fi

.PHONY: help up down restart status logs logs-ingestion logs-gateway logs-frontend shell build clean stats db-shell db-backup env
