#!/bin/bash

# Directorio que deseas verificar
TARGET_DIRECTORY="./proto_app/backend/"

flake8 --max-line-length=200 $TARGET_DIRECTORY

# Guarda el código de salida de Flake8
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  exit 1
else
  echo "No flake issues found in the Python code"
fi