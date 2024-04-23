#!/bin/bash

TARGET_DIRECTORY="."

echo "Checking Python code with radon..."
RADON_OUTPUT=$(radon cc $TARGET_DIRECTORY --average -s)

# Capturar la salida y extraer el puntaje promedio de complejidad ciclomática
# Suponiendo que radon entrega la salida en un formato como: 'Average complexity: A (1.5)'
# Vamos a extraer '1.5' usando awk y sed
AVG_SCORE=$(echo "$RADON_OUTPUT" | grep 'Average complexity' | awk '{print $4}' | sed 's/[^0-9.]*//g')
SCORE_INT=$(echo "$AVG_SCORE" | awk -F. '{print $1}')

# Verificar si el puntaje promedio es menor a 10
if [ "$SCORE_INT" -lt 10 ]; then
    echo "Radon cc avg score ($AVG_SCORE) is good (less than 10)."
else
    echo "Average complexity is 10 or greater, which is not acceptable."
    exit 1
fi
