@echo off
REM ============================================================================
REM Script para gestionar la plataforma con Docker (Windows)
REM Uso: docker-manage.bat [comando]
REM ============================================================================

setlocal enabledelayedexpansion

REM Colores para output (Windows 10+)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Verificar si estamos en el directorio correcto
if not exist docker-compose.yml (
    echo %RED%[ERROR]%NC% docker-compose.yml no encontrado
    echo Por favor ejecuta este script desde el directorio raíz del proyecto
    exit /b 1
)

REM Verificar si Docker está instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Docker no está instalado
    exit /b 1
)

REM Crear .env si no existe
if not exist .env (
    echo %YELLOW%[ADVERTENCIA]%NC% .env no encontrado
    if exist .env.example (
        echo Creando .env desde .env.example...
        copy .env.example .env >nul
        echo %BLUE%[INFO]%NC% Edita .env con tus variables de entorno
    )
)

REM Procesar comando
if "%1"=="" goto help
if "%1"=="up" goto cmd_up
if "%1"=="down" goto cmd_down
if "%1"=="restart" goto cmd_restart
if "%1"=="logs" goto cmd_logs
if "%1"=="status" goto cmd_status
if "%1"=="shell" goto cmd_shell
if "%1"=="build" goto cmd_build
if "%1"=="clean" goto cmd_clean
if "%1"=="db-backup" goto cmd_db_backup
if "%1"=="db-shell" goto cmd_db_shell
if "%1"=="stats" goto cmd_stats
if "%1"=="help" goto help
if "%1"=="-h" goto help
if "%1"=="--help" goto help

echo %RED%[ERROR]%NC% Comando no reconocido: %1
goto help

:cmd_up
echo %BLUE%[INFO]%NC% Levantando servicios...
docker-compose up -d --build
if errorlevel 1 goto error
echo %GREEN%[OK]%NC% Plataforma levantada
echo %BLUE%[INFO]%NC% Frontend: http://localhost:5173
echo %BLUE%[INFO]%NC% API: http://localhost:8001
echo %BLUE%[INFO]%NC% Docs: http://localhost:8001/docs
goto end

:cmd_down
echo %BLUE%[INFO]%NC% Deteniendo servicios...
docker-compose down
if errorlevel 1 goto error
echo %GREEN%[OK]%NC% Servicios detenidos
goto end

:cmd_restart
echo %BLUE%[INFO]%NC% Reiniciando servicios...
docker-compose restart
if errorlevel 1 goto error
echo %GREEN%[OK]%NC% Servicios reiniciados
goto end

:cmd_logs
if "%2"=="" (
    echo %BLUE%[INFO]%NC% Mostrando logs de todos los servicios...
    docker-compose logs -f --tail=100
) else (
    echo %BLUE%[INFO]%NC% Mostrando logs de %2...
    docker-compose logs -f --tail=100 %2
)
goto end

:cmd_status
echo %BLUE%[INFO]%NC% Estado de los servicios:
docker-compose ps
goto end

:cmd_shell
if "%2"=="" (
    echo %RED%[ERROR]%NC% Especifica servicio: docker-manage.bat shell [servicio]
    echo %BLUE%[INFO]%NC% Servicios disponibles:
    docker-compose ps --services
    exit /b 1
)
echo %BLUE%[INFO]%NC% Conectando a %2...
docker-compose exec %2 bash
goto end

:cmd_build
if "%2"=="" (
    echo %BLUE%[INFO]%NC% Construyendo todas las imágenes...
    docker-compose build
) else (
    echo %BLUE%[INFO]%NC% Construyendo %2...
    docker-compose build %2
)
if errorlevel 1 goto error
echo %GREEN%[OK]%NC% Construcción completada
goto end

:cmd_clean
setlocal enabledelayedexpansion
echo %YELLOW%[ADVERTENCIA]%NC% Esto eliminará contenedores, imágenes y volúmenes
set /p response="¿Estás seguro? (s/n): "
if /i "!response!"=="s" (
    echo %BLUE%[INFO]%NC% Limpiando...
    docker-compose down -v
    if errorlevel 1 goto error
    echo %GREEN%[OK]%NC% Limpieza completada
) else (
    echo %BLUE%[INFO]%NC% Cancelado
)
endlocal
goto end

:cmd_db_backup
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c%%a%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a%%b)
set backup_file=backup-!mydate!_!mytime!.sql
echo %BLUE%[INFO]%NC% Creando backup de base de datos: !backup_file!
docker-compose exec -T db-postgres pg_dump -U postgres territorial_db > !backup_file!
if errorlevel 1 goto error
echo %GREEN%[OK]%NC% Backup creado: !backup_file!
goto end

:cmd_db_shell
echo %BLUE%[INFO]%NC% Conectando a PostgreSQL...
docker-compose exec db-postgres psql -U postgres -d territorial_db
goto end

:cmd_stats
echo %BLUE%[INFO]%NC% Estadísticas de uso:
docker stats
goto end

:help
echo.
echo %BLUE%Gestor de Plataforma con Docker%NC%
echo.
echo Uso: docker-manage.bat [comando] [opciones]
echo.
echo %GREEN%Comandos Principales:%NC%
echo   up              Levantar todos los servicios
echo   down            Detener todos los servicios
echo   restart         Reiniciar todos los servicios
echo   status          Ver estado de los servicios
echo   logs [service]  Ver logs (todos o de un servicio)
echo.
echo %GREEN%Desarrollo:%NC%
echo   shell [service] Conectar a terminal de un servicio
echo   build [service] Construir imágenes (todas o una específica)
echo   clean           Limpiar contenedores, imágenes y volúmenes
echo.
echo %GREEN%Base de Datos:%NC%
echo   db-shell        Conectar a PostgreSQL
echo   db-backup       Crear backup de base de datos
echo.
echo %GREEN%Monitoreo:%NC%
echo   stats           Ver uso de recursos en tiempo real
echo.
echo %GREEN%Ejemplos:%NC%
echo   docker-manage.bat up
echo   docker-manage.bat logs ms-ingestion
echo   docker-manage.bat shell bff-gateway
echo   docker-manage.bat db-backup
echo.
goto end

:error
echo %RED%[ERROR]%NC% El comando falló
exit /b 1

:end
exit /b 0
