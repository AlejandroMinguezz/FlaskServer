# ====================================
# SCRIPT DE INICIO DE BASES DE DATOS
# ====================================
# Inicia PostgreSQL y MongoDB en Docker

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  DirectIA - Inicio de Bases de Datos" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que Docker esté instalado
Write-Host "[1/3] Verificando Docker..." -ForegroundColor Yellow
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker no está instalado o no está en el PATH" -ForegroundColor Red
    exit 1
}
Write-Host "Docker encontrado" -ForegroundColor Green

# Verificar que Docker esté corriendo
Write-Host "[2/3] Verificando que Docker esté corriendo..." -ForegroundColor Yellow
docker ps > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker no está corriendo. Por favor inicia Docker Desktop" -ForegroundColor Red
    exit 1
}
Write-Host "Docker está corriendo" -ForegroundColor Green

# Iniciar contenedores
Write-Host "[3/3] Iniciando bases de datos..." -ForegroundColor Yellow
Set-Location docker
docker-compose up -d
Set-Location ..

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Green
    Write-Host "  Bases de datos iniciadas!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "PostgreSQL: localhost:5432" -ForegroundColor Cyan
    Write-Host "MongoDB:    localhost:27017" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "NOTA: Los datos se almacenan en volúmenes Docker:" -ForegroundColor Yellow
    Write-Host "  - directia_postgres_data" -ForegroundColor White
    Write-Host "  - directia_mongo_data" -ForegroundColor White
    Write-Host ""
    Write-Host "Para ver los logs:" -ForegroundColor Yellow
    Write-Host "  docker logs -f directia_postgres" -ForegroundColor White
    Write-Host "  docker logs -f directia_mongo" -ForegroundColor White
    Write-Host ""
    Write-Host "Para detener:" -ForegroundColor Yellow
    Write-Host "  cd docker && docker-compose down" -ForegroundColor White
    Write-Host ""
    Write-Host "Para eliminar los datos (¡CUIDADO!):" -ForegroundColor Red
    Write-Host "  cd docker && docker-compose down -v" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "ERROR: No se pudieron iniciar las bases de datos" -ForegroundColor Red
    exit 1
}
