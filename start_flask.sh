#!/bin/bash
# ====================================
# SCRIPT DE INICIO DE FLASK
# ====================================
# Inicia el servidor Flask localmente

echo "=================================="
echo "  DirectIA - Inicio de Flask"
echo "=================================="
echo ""

# Verificar que Python esté instalado
echo "[1/4] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python no está instalado o no está en el PATH"
    exit 1
fi
pythonVersion=$(python3 --version)
echo "Python encontrado: $pythonVersion"

# Verificar que exista el archivo .env
echo "[2/4] Verificando configuración..."
if [ ! -f ".env" ]; then
    echo "ADVERTENCIA: No se encontró el archivo .env"
    echo "Se usarán valores por defecto"
else
    echo "Archivo .env encontrado"
fi

# Verificar que las bases de datos estén corriendo
echo "[3/4] Verificando bases de datos..."
postgresRunning=$(docker ps --filter "name=directia_postgres" --filter "status=running" -q)
mongoRunning=$(docker ps --filter "name=directia_mongo" --filter "status=running" -q)

if [ -z "$postgresRunning" ] || [ -z "$mongoRunning" ]; then
    echo "ADVERTENCIA: Las bases de datos no están corriendo"
    echo "Ejecuta './start_databases.sh' primero"
    read -p "¿Continuar de todas formas? (s/n) " continue
    if [ "$continue" != "s" ] && [ "$continue" != "S" ]; then
        exit 1
    fi
else
    echo "Bases de datos corriendo"
fi

# Iniciar Flask
echo "[4/4] Iniciando Flask..."
echo ""
echo "=================================="
echo "  Servidor Flask iniciado!"
echo "=================================="
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

# Establecer PYTHONPATH para que encuentre el módulo src
export PYTHONPATH=$PWD
python3 -m src.app
