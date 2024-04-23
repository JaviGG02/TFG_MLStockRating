#!/bin/bash

PYTHONPATH=./proto_app/backend pytest -W ignore::DeprecationWarning ./proto_app/backend/tests

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Las pruebas unitarias encontraron errores."
    exit $EXIT_CODE
else
    echo "All unit tests passed!"
fi