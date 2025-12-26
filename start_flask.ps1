# ====================================
# SCRIPT DE INICIO DE FLASK
# ====================================
# Inicia el servidor Flask localmente

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  DirectIA - Inicio de Flask" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que Python esté instalado
Write-Host "[1/4] Verificando Python..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    exit 1
}
$pythonVersion = python --version
Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green

# Verificar que exista el archivo .env
Write-Host "[2/4] Verificando configuración..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "ADVERTENCIA: No se encontró el archivo .env" -ForegroundColor Yellow
    Write-Host "Se usarán valores por defecto" -ForegroundColor Yellow
} else {
    Write-Host "Archivo .env encontrado" -ForegroundColor Green
}

# Verificar que las bases de datos estén corriendo
Write-Host "[3/4] Verificando bases de datos..." -ForegroundColor Yellow
$postgresRunning = docker ps --filter "name=directia_postgres" --filter "status=running" -q
$mongoRunning = docker ps --filter "name=directia_mongo" --filter "status=running" -q

if (-not $postgresRunning -or -not $mongoRunning) {
    Write-Host "ADVERTENCIA: Las bases de datos no están corriendo" -ForegroundColor Yellow
    Write-Host "Ejecuta './start_databases.ps1' primero" -ForegroundColor Yellow
    $continue = Read-Host "¿Continuar de todas formas? (s/n)"
    if ($continue -ne "s" -and $continue -ne "S") {
        exit 1
    }
} else {
    Write-Host "Bases de datos corriendo" -ForegroundColor Green
}

# Iniciar Flask
Write-Host "[4/4] Iniciando Flask..." -ForegroundColor Yellow
Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "  Servidor Flask iniciado!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Establecer PYTHONPATH para que encuentre el módulo src
$env:PYTHONPATH = $PWD
python -m src.app
