#!/bin/bash
# ====================================
# SCRIPT DE INICIO DE BASES DE DATOS
# ====================================
# Inicia PostgreSQL y MongoDB en Docker

echo "=================================="
echo "  DirectIA - Inicio de Bases de Datos"
echo "=================================="
echo ""

# Verificar que Docker esté instalado
echo "[1/3] Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker no está instalado o no está en el PATH"
    exit 1
fi
echo "Docker encontrado"

# Verificar que Docker esté corriendo
echo "[2/3] Verificando que Docker esté corriendo..."
if ! docker ps &> /dev/null; then
    echo "ERROR: Docker no está corriendo. Por favor inicia Docker"
    exit 1
fi
echo "Docker está corriendo"

# Iniciar contenedores
echo "[3/3] Iniciando bases de datos..."
cd docker
docker-compose up -d
cd ..

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "  Bases de datos iniciadas!"
    echo "=================================="
    echo ""
    echo "PostgreSQL: localhost:5432"
    echo "MongoDB:    localhost:27017"
    echo ""
    echo "NOTA: Los datos se almacenan en volúmenes Docker:"
    echo "  - directia_postgres_data"
    echo "  - directia_mongo_data"
    echo ""
    echo "Para ver los logs:"
    echo "  docker logs -f directia_postgres"
    echo "  docker logs -f directia_mongo"
    echo ""
    echo "Para detener:"
    echo "  cd docker && docker-compose down"
    echo ""
    echo "Para eliminar los datos (¡CUIDADO!):"
    echo "  cd docker && docker-compose down -v"
else
    echo ""
    echo "ERROR: No se pudieron iniciar las bases de datos"
    exit 1
fi
