"""
Bateria de pruebas para el backend de la app
"""

# pylint: disable=C0413,E0401,E0402,W0621
import pathlib
import pytest
from flask import json
from app import app
from jsonschema import validate
from jsonschema.exceptions import ValidationError


@pytest.fixture
def client():
    """
    Metodo para la gestion de los tests a la app
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def validate_payload(payload, schema_name):
    """
    Funcion auxiliar para validar el esquema de un objeto
    """
    schemas_dir = str(f"{pathlib.Path(__file__).parent.absolute()}/schemas")
    schema = json.loads(
        pathlib.Path(f"{schemas_dir}/{schema_name}").read_text(encoding="utf-8")
    )
    try:
        return validate(payload, schema)
    except ValidationError as e:
        return pytest.fail(f"Esquema JSON incorrecto: {e.message}")


def test_api_ticker_valido(client):
    """
    Test ID: TU-APP-01
    Covered Requirement: RF-08: Peticiones satisfactorias al backend

    Este test verifica que el sistema es capaz de hacer peticiones al backend
    para una acción dada, asegurando que se llevan a cabo los procesos de
    recoleccion y preprocesamiento de datos, realizacion de predicciones
    y calificacion y preparacion de la respuesta.

    Metodología: Se simula una petición POST a la API pasando
    como parámetro el símbolo de una empresa conocida. Se verifica que la respuesta
    contiene todos los campos esperados.

    Salida Esperada: El sistema debe devolver un JSON con la estructura correcta y completa,
    incluyendo los datos financieros, la calificacion y la prediccion computadas.
    """
    response = client.post(
        "/api/datos",
        data=json.dumps({"ticker": "AAPL"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)

    validate_payload(data, "schema_response.json")


def test_api_ticker_invalido(client):
    """
    Test ID: TU-APP-02
    Covered Requirement:
        RF-09: Manejo de tickers inválidos
        RNF-03: Tratamiento de errores

    Este test verifica que el sistema maneja correctamente los casos en que se
    proporciona un ticker inválido, asegurando que se devuelva un mensaje de error
    apropiado y que no se produzcan datos incorrectos.

    Metodología: Se simula una petición POST al módulo de recolección de datos pasando
    como parámetro un símbolo de empresa inválido. Se verifica que la respuesta contenga
    un mensaje de error claro y no datos financieros.

    Salida Esperada: El sistema debe devolver un JSON que contenga un mensaje de error
    indicando que el ticker no es válido o no se encontraron datos para el mismo.
    """
    response = client.post(
        "/api/datos",
        data=json.dumps({"ticker": "INVALID"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)

    assert "Error" in data
    assert data["Error"] == "Ticker (INVALID) data not available"
