#!/bin/bash

TARGET_FILES="./proto_app/backend/app.py ./proto_app/backend/data_manager.py ./proto_app/backend/data_manager_aux.py"

PYLINT_OUTPUT=$(pylint $TARGET_FILES)
EXIT_CODE=$?

# Parsear la puntuación de salida de pylint
PYLINT_SCORE=$(echo "$PYLINT_OUTPUT" | grep "Your code has been rated at" | awk '{print $7}' | sed 's/\/10.00//')
# Convertir la puntuación a un número entero (removiendo el punto decimal)
PYLINT_SCORE_INT=$(echo "$PYLINT_SCORE" | awk -F. '{print $1}')

# Verificar si la puntuación es menor que 7
if [ "$PYLINT_SCORE_INT" -lt 7 ]; then
  echo "Pylint score ($PYLINT_SCORE) is not sufficient (less than 7)."
  exit 1
else
  echo "Pylint score ($PYLINT_SCORE) is good (greater than 7)."
  exit 0
fi
