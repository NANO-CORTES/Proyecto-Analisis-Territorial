#!/bin/bash
# ============================================================================
# Script para gestionar la plataforma con Docker
# Uso: ./docker-manage.sh [comando]
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones auxiliares
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Verificar si Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado"
        exit 1
    fi
    
    print_success "Docker y Docker Compose están instalados"
}

# Crear .env si no existe
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env no encontrado, creando desde .env.example"
        cp .env.example .env
        print_info "Edita .env con tus variables de entorno"
    fi
}

# Comandos disponibles
cmd_up() {
    print_info "Levantando servicios..."
    docker-compose up -d --build
    print_success "Plataforma levantada"
    print_info "Frontend: http://localhost:5173"
    print_info "API: http://localhost:8001"
    print_info "Docs: http://localhost:8001/docs"
}

cmd_down() {
    print_info "Deteniendo servicios..."
    docker-compose down
    print_success "Servicios detenidos"
}

cmd_restart() {
    print_info "Reiniciando servicios..."
    docker-compose restart
    print_success "Servicios reiniciados"
}

cmd_logs() {
    if [ -z "$2" ]; then
        print_info "Mostrando logs de todos los servicios..."
        docker-compose logs -f --tail=100
    else
        print_info "Mostrando logs de $2..."
        docker-compose logs -f --tail=100 "$2"
    fi
}

cmd_status() {
    print_info "Estado de los servicios:"
    docker-compose ps
}

cmd_shell() {
    if [ -z "$2" ]; then
        print_error "Especifica servicio: ./docker-manage.sh shell [servicio]"
        print_info "Servicios disponibles:"
        docker-compose ps --services
        exit 1
    fi
    
    print_info "Conectando a $2..."
    docker-compose exec "$2" bash
}

cmd_build() {
    if [ -z "$2" ]; then
        print_info "Construyendo todas las imágenes..."
        docker-compose build
    else
        print_info "Construyendo $2..."
        docker-compose build "$2"
    fi
    print_success "Construcción completada"
}

cmd_clean() {
    print_warning "Esto eliminará contenedores, imágenes y volúmenes"
    read -p "¿Estás seguro? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        print_info "Limpiando..."
        docker-compose down -v
        print_success "Limpieza completada"
    else
        print_info "Cancelado"
    fi
}

cmd_db_backup() {
    BACKUP_FILE="backup-$(date +%Y%m%d_%H%M%S).sql"
    print_info "Creando backup de base de datos: $BACKUP_FILE"
    docker-compose exec -T db-postgres pg_dump -U postgres territorial_db > "$BACKUP_FILE"
    print_success "Backup creado: $BACKUP_FILE"
}

cmd_db_shell() {
    print_info "Conectando a PostgreSQL..."
    docker-compose exec db-postgres psql -U postgres -d territorial_db
}

cmd_stats() {
    print_info "Estadísticas de uso:"
    docker stats
}

cmd_help() {
    cat << EOF
${BLUE}Gestor de Plataforma con Docker${NC}

Uso: ./docker-manage.sh [comando] [opciones]

${GREEN}Comandos Principales:${NC}
  up              Levantar todos los servicios
  down            Detener todos los servicios
  restart         Reiniciar todos los servicios
  status          Ver estado de los servicios
  logs [service]  Ver logs (todos o de un servicio)

${GREEN}Desarrollo:${NC}
  shell [service] Conectar a terminal de un servicio
  build [service] Construir imágenes (todas o una específica)
  clean           Limpiar contenedores, imágenes y volúmenes

${GREEN}Base de Datos:${NC}
  db-shell        Conectar a PostgreSQL
  db-backup       Crear backup de base de datos

${GREEN}Monitoreo:${NC}
  stats           Ver uso de recursos en tiempo real

${GREEN}Ejemplos:${NC}
  ./docker-manage.sh up
  ./docker-manage.sh logs ms-ingestion
  ./docker-manage.sh shell bff-gateway
  ./docker-manage.sh db-backup

EOF
}

# Main
main() {
    check_docker
    check_env
    
    case "${1:-help}" in
        up)
            cmd_up
            ;;
        down)
            cmd_down
            ;;
        restart)
            cmd_restart
            ;;
        logs)
            cmd_logs "$@"
            ;;
        status)
            cmd_status
            ;;
        shell)
            cmd_shell "$@"
            ;;
        build)
            cmd_build "$@"
            ;;
        clean)
            cmd_clean
            ;;
        db-backup)
            cmd_db_backup
            ;;
        db-shell)
            cmd_db_shell
            ;;
        stats)
            cmd_stats
            ;;
        help|--help|-h)
            cmd_help
            ;;
        *)
            print_error "Comando no reconocido: $1"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
