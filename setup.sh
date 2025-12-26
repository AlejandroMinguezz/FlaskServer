#!/bin/bash
# ====================================
# SCRIPT DE SETUP INICIAL - DirectIA
# ====================================
# Configura el entorno de desarrollo completo

echo "=========================================="
echo "  DirectIA - Setup Inicial"
echo "=========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ====================================
# 1. Verificar Python
# ====================================
echo -e "${YELLOW}[1/8] Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 no está instalado${NC}"
    echo "Por favor instala Python 3.8 o superior desde https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION encontrado${NC}"

# ====================================
# 2. Verificar pip
# ====================================
echo -e "${YELLOW}[2/8] Verificando pip...${NC}"
if ! python3 -m pip --version &> /dev/null; then
    echo -e "${RED}ERROR: pip no está instalado${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip encontrado${NC}"

# ====================================
# 3. Crear entorno virtual
# ====================================
echo -e "${YELLOW}[3/8] Configurando entorno virtual...${NC}"
if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Entorno virtual creado${NC}"
    else
        echo -e "${RED}ERROR: No se pudo crear el entorno virtual${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Entorno virtual ya existe${NC}"
fi

# ====================================
# 4. Activar entorno virtual e instalar dependencias
# ====================================
echo -e "${YELLOW}[4/8] Instalando dependencias...${NC}"
source .venv/bin/activate

if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}ERROR: requirements.txt no encontrado${NC}"
    exit 1
fi

echo "Instalando paquetes de Python..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencias instaladas${NC}"
else
    echo -e "${RED}ERROR: Falló la instalación de dependencias${NC}"
    exit 1
fi

# ====================================
# 5. Verificar Tesseract OCR
# ====================================
echo -e "${YELLOW}[5/8] Verificando Tesseract OCR...${NC}"
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n 1)
    echo -e "${GREEN}✓ $TESSERACT_VERSION${NC}"

    # Verificar idioma español
    if tesseract --list-langs 2>&1 | grep -q "spa"; then
        echo -e "${GREEN}✓ Idioma español (spa) instalado${NC}"
    else
        echo -e "${YELLOW}⚠ Advertencia: Idioma español no encontrado${NC}"
        echo "Para instalar:"
        echo "  macOS: brew install tesseract-lang"
        echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr-spa"
    fi
else
    echo -e "${YELLOW}⚠ Tesseract OCR no está instalado${NC}"
    echo "El OCR no funcionará sin Tesseract. Para instalar:"
    echo "  macOS: brew install tesseract tesseract-lang"
    echo "  Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-spa"
    echo ""
    echo -e "${YELLOW}Continuando sin Tesseract...${NC}"
fi

# ====================================
# 6. Crear directorios necesarios
# ====================================
echo -e "${YELLOW}[6/8] Creando directorios necesarios...${NC}"
mkdir -p ../storage/files
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Directorio de almacenamiento creado${NC}"
else
    echo -e "${RED}ERROR: No se pudo crear el directorio de almacenamiento${NC}"
    exit 1
fi

# ====================================
# 7. Verificar archivos de configuración
# ====================================
echo -e "${YELLOW}[7/8] Verificando configuración...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ Archivo .env no encontrado${NC}"
    echo "Por favor crea un archivo .env en la raíz del proyecto"
    echo "Puedes usar .env.example como plantilla si existe"
else
    echo -e "${GREEN}✓ Archivo .env encontrado${NC}"
fi

if [ ! -f "docker/.env" ]; then
    echo -e "${YELLOW}⚠ Archivo docker/.env no encontrado${NC}"
else
    echo -e "${GREEN}✓ Archivo docker/.env encontrado${NC}"
fi

# ====================================
# 8. Verificar Docker
# ====================================
echo -e "${YELLOW}[8/8] Verificando Docker...${NC}"
if command -v docker &> /dev/null; then
    if docker ps &> /dev/null; then
        echo -e "${GREEN}✓ Docker está instalado y corriendo${NC}"
    else
        echo -e "${YELLOW}⚠ Docker está instalado pero no está corriendo${NC}"
        echo "Por favor inicia Docker Desktop"
    fi
else
    echo -e "${YELLOW}⚠ Docker no está instalado${NC}"
    echo "Necesitas Docker para las bases de datos"
    echo "Descarga desde: https://www.docker.com/products/docker-desktop"
fi

# ====================================
# Finalización
# ====================================
echo ""
echo "=========================================="
echo -e "${GREEN}  ✓ Setup completado!${NC}"
echo "=========================================="
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Iniciar bases de datos:"
echo "   ./start_databases.sh"
echo ""
echo "2. Iniciar Flask:"
echo "   ./start_flask.sh"
echo ""
echo "3. Acceder a la aplicación:"
echo "   http://localhost:5001"
echo ""
echo "Nota: El entorno virtual está activado en esta sesión."
echo "Para activarlo en nuevas terminales:"
echo "   source .venv/bin/activate"
echo ""
