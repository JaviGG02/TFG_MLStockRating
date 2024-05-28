#!/bin/bash

# Ejecutar Prettier para verificar el formato del código
npx prettier --write "**/*.{js,jsx,html,css}"

# Capturar el código de salida de Prettier
EXIT_CODE=$?

# Si Prettier encuentra un problema (código de salida no es 0), devuelve error
if [ $EXIT_CODE -ne 0 ]; then
  echo "Error de formato en los archivos, revisar Prettier"
  exit $EXIT_CODE
fi

echo "Todos los archivos están correctamente formateados."
