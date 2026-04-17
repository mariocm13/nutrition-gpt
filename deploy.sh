#!/bin/bash

# Script de automatización para NutriGPT
# Uso: ./deploy.sh "Mensaje del commit"

# Colores para la consola
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando proceso de actualización para NutriGPT...${NC}"

# 1. Verificar si se proporcionó un mensaje de commit
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: Debes proporcionar un mensaje para el commit.${NC}"
    echo "Uso: ./deploy.sh \"Descripción de los cambios\""
    exit 1
fi

# 2. Validar sintaxis de Python (opcional pero recomendado)
echo -e "${BLUE}🔍 Validando sintaxis del código...${NC}"
python3 -m py_compile app.py nlp_processor.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Sintaxis correcta.${NC}"
else
    echo -e "${RED}❌ Error de sintaxis en el código. Abortando.${NC}"
    exit 1
fi

# 3. Sincronizar con GitHub
echo -e "${BLUE}📦 Subiendo cambios a GitHub...${NC}"
git add .
git commit -m "$1"
git push origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Cambios subidos con éxito a GitHub.${NC}"
    echo -e "${GREEN}🚀 Render detectará los cambios y comenzará el despliegue automáticamente.${NC}"
    echo -e "${BLUE}🔗 Puedes seguir el progreso en: https://dashboard.render.com/${NC}"
else
    echo -e "${RED}❌ Error al subir a GitHub. Verifica tu conexión o permisos.${NC}"
    exit 1
fi

echo -e "${BLUE}✨ ¡Proceso completado! Tu NutriGPT se actualizará en unos minutos.${NC}"
