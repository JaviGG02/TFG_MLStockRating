"""
Bateria de pruebas para el backend de la app
"""
# pylint: disable=C0413,E0401,E0402,W0621
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import pytest
from flask import json
from app import app

@pytest.fixture
def client():
    """
    Metodo para la gestion de los tests a la app
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_api_ticker_valido(client):
    """
    Test ID: TU-0
    Covered Requirement: RF-06: Peticiones satisfactorias al backend

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
    financial_data_attributes = [
        "datos_financieros",
        "calificacion",
        "prediccion",
    ]

    response = client.post(
        "/api/datos",
        data=json.dumps({"ticker": "AAPL"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = json.loads(response.data)

    assert "Error" not in data
    for attribute in financial_data_attributes:
        assert attribute in data


def test_api_ticker_invalido(client):
    """
    Test ID: TU-0
    Covered Requirement: RF-07: Manejo de tickers inválidos

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
    assert data["Error"] == "Información sobre INVALID no disponible"
