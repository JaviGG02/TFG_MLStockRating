#!/bin/bash

# Directorio que deseas verificar para problemas de seguridad
TARGET_DIRECTORY="./proto_app/backend"
pwd
echo $TARGET_DIRECTORY
bandit -r --exclude ./proto_app/backend/tests $TARGET_DIRECTORY --format txt --output bandit_security_report.txt

EXIT_CODE=$?

# Bandit establece el código de salida a 1 si se encuentran problemas de seguridad
if [ $EXIT_CODE -ne 0 ]; then
    echo "Bandit encontró problemas de seguridad."
    echo "Revisar el reporte en 'bandit_report.txt' para más detalles."
    exit $EXIT_CODE
else
    echo "No bandit issues found in Python code."
fi
