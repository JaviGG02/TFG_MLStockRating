#!/bin/bash

# Ejecutar ESLint para verificar la calidad del código JavaScript/React
npx eslint . --config proto_app/.eslintrc.json

# Capturar el código de salida de ESLint
EXIT_CODE=$?

# Si ESLint encuentra un problema (código de salida no es 0), devuelve error
if [ $EXIT_CODE -ne 0 ]; then
  echo "Errores de ESLint detectados, revisar los detalles arriba."
  exit $EXIT_CODE
fi

echo "No se detectaron problemas con ESLint."