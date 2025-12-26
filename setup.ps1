# ====================================
# SCRIPT DE SETUP INICIAL - DirectIA
# ====================================
# Configura el entorno de desarrollo completo

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  DirectIA - Setup Inicial" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ====================================
# 1. Verificar Python
# ====================================
Write-Host "[1/8] Verificando Python..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python 3 no está instalado" -ForegroundColor Red
    Write-Host "Por favor instala Python 3.8 o superior desde https://www.python.org/" -ForegroundColor Red
    exit 1
}

$pythonVersion = (python --version 2>&1).ToString().Split()[1]
Write-Host "✓ Python $pythonVersion encontrado" -ForegroundColor Green

# ====================================
# 2. Verificar pip
# ====================================
Write-Host "[2/8] Verificando pip..." -ForegroundColor Yellow
python -m pip --version > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pip no está instalado" -ForegroundColor Red
    exit 1
}
Write-Host "✓ pip encontrado" -ForegroundColor Green

# ====================================
# 3. Crear entorno virtual
# ====================================
Write-Host "[3/8] Configurando entorno virtual..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    Write-Host "Creando entorno virtual..." -ForegroundColor White
    python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Entorno virtual creado" -ForegroundColor Green
    } else {
        Write-Host "ERROR: No se pudo crear el entorno virtual" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Entorno virtual ya existe" -ForegroundColor Green
}

# ====================================
# 4. Activar entorno virtual e instalar dependencias
# ====================================
Write-Host "[4/8] Instalando dependencias..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

if (-not (Test-Path "requirements.txt")) {
    Write-Host "ERROR: requirements.txt no encontrado" -ForegroundColor Red
    exit 1
}

Write-Host "Instalando paquetes de Python..." -ForegroundColor White
python -m pip install --upgrade pip > $null 2>&1
python -m pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencias instaladas" -ForegroundColor Green
} else {
    Write-Host "ERROR: Falló la instalación de dependencias" -ForegroundColor Red
    exit 1
}

# ====================================
# 5. Verificar Tesseract OCR
# ====================================
Write-Host "[5/8] Verificando Tesseract OCR..." -ForegroundColor Yellow
if (Get-Command tesseract -ErrorAction SilentlyContinue) {
    $tesseractVersion = (tesseract --version 2>&1 | Select-Object -First 1).ToString()
    Write-Host "✓ $tesseractVersion" -ForegroundColor Green

    # Verificar idioma español
    $langs = tesseract --list-langs 2>&1 | Out-String
    if ($langs -match "spa") {
        Write-Host "✓ Idioma español (spa) instalado" -ForegroundColor Green
    } else {
        Write-Host "⚠ Advertencia: Idioma español no encontrado" -ForegroundColor Yellow
        Write-Host "Para instalar el idioma español, descarga los archivos de idioma desde:" -ForegroundColor White
        Write-Host "https://github.com/tesseract-ocr/tessdata" -ForegroundColor White
    }
} else {
    Write-Host "⚠ Tesseract OCR no está instalado" -ForegroundColor Yellow
    Write-Host "El OCR no funcionará sin Tesseract. Para instalar:" -ForegroundColor White
    Write-Host "1. Descarga el instalador desde: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
    Write-Host "2. Instala Tesseract y añade al PATH del sistema" -ForegroundColor White
    Write-Host ""
    Write-Host "Continuando sin Tesseract..." -ForegroundColor Yellow
}

# ====================================
# 6. Crear directorios necesarios
# ====================================
Write-Host "[6/8] Creando directorios necesarios..." -ForegroundColor Yellow
$storagePath = "..\storage\files"
if (-not (Test-Path $storagePath)) {
    New-Item -ItemType Directory -Path $storagePath -Force > $null
}
if (Test-Path $storagePath) {
    Write-Host "✓ Directorio de almacenamiento creado" -ForegroundColor Green
} else {
    Write-Host "ERROR: No se pudo crear el directorio de almacenamiento" -ForegroundColor Red
    exit 1
}

# ====================================
# 7. Verificar archivos de configuración
# ====================================
Write-Host "[7/8] Verificando configuración..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠ Archivo .env no encontrado" -ForegroundColor Yellow
    Write-Host "Por favor crea un archivo .env en la raíz del proyecto" -ForegroundColor White
    Write-Host "Puedes usar .env.example como plantilla si existe" -ForegroundColor White
} else {
    Write-Host "✓ Archivo .env encontrado" -ForegroundColor Green
}

if (-not (Test-Path "docker\.env")) {
    Write-Host "⚠ Archivo docker\.env no encontrado" -ForegroundColor Yellow
} else {
    Write-Host "✓ Archivo docker\.env encontrado" -ForegroundColor Green
}

# ====================================
# 8. Verificar Docker
# ====================================
Write-Host "[8/8] Verificando Docker..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker ps > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker está instalado y corriendo" -ForegroundColor Green
    } else {
        Write-Host "⚠ Docker está instalado pero no está corriendo" -ForegroundColor Yellow
        Write-Host "Por favor inicia Docker Desktop" -ForegroundColor White
    }
} else {
    Write-Host "⚠ Docker no está instalado" -ForegroundColor Yellow
    Write-Host "Necesitas Docker para las bases de datos" -ForegroundColor White
    Write-Host "Descarga desde: https://www.docker.com/products/docker-desktop" -ForegroundColor White
}

# ====================================
# Finalización
# ====================================
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ✓ Setup completado!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Iniciar bases de datos:" -ForegroundColor White
Write-Host "   .\start_databases.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Iniciar Flask:" -ForegroundColor White
Write-Host "   .\start_flask.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Acceder a la aplicación:" -ForegroundColor White
Write-Host "   http://localhost:5001" -ForegroundColor Yellow
Write-Host ""
Write-Host "Nota: El entorno virtual está activado en esta sesión." -ForegroundColor White
Write-Host "Para activarlo en nuevas terminales:" -ForegroundColor White
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
