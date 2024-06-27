"""
Bateria de pruebas para el modulo de data_manager del backend
"""

# pylint: disable=C0413,E0401,E0402,W0621
import json
import pathlib
from data_manager import DataManager
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import pytest


@pytest.fixture(scope="module")
def data_manager():
    """
    Fixture de pytest para crear una instancia de DataManager y descargar datos.
    """
    dm = DataManager(ticker="AAPL")
    # Simula la descarga de datos financieros una sola vez y los almacena
    dm.financial_data = dm.download_financial_data()
    dm.preprocessed_data = dm.preprocess_financial_data()
    dm.predictions = dm.make_predictions()
    dm.ratings = dm.calculate_rating()
    return dm


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


def test_recoleccion_datos_historicos(data_manager):
    """
    Test ID: TU-DM-1
    Requisito cubierto: RF-06: Peticiones satisfactorias al backend

    Este test verifica que el sistema es capaz de recolectar datos históricos de acciones
    para diversas empresas, asegurando que los datos financieros como el histórico de precios
    mensual ajustado, estados financieros y descripción general están presentes en la
    respuesta obtenida.

    Metodología: Se ejecuta la función download_financial_data() del data_manager, simulando
    la descarga de datos financieros y se compara con un esquema predefinido con los datos
    mínimos necesarios.

    Salida esperada: La función debe devolver un diccionario que contenga todos los atributos
    financieros especificados, validando la capacidad del sistema para procesar y recolectar
    los datos financieros requeridos.
    """
    validate_payload(data_manager.financial_data, "schema_financial_data.json")


def test_preprocesamiento_datos(data_manager):
    """
    Test ID: TU-DM-02
    Requisito cubierto: RF-02: Preprocesamiento de los datos

    Este test verifica que el sistema es capaz de transformar adecuadamente los datos descargados
    para ser procesados por el modelo de predicción, asegurando que se generen las estructuras
    necesarias para realizar predicciones eficaces.

    Metodología: Utiliza los datos descargados previamente almacenados en la fixture para
    ejecutar la función preprocess_financial_data().
    Salida esperada: Los datos preprocesados han de tener las mismas columnas que el modelo que
    se empleo durante el entrenamiento.
    """
    attributes_required = [
        "fiscalDateEnding",
        "totalAssets",
        "commonStock",
        "retainedEarnings",
        "totalShareholderEquity",
        "incomeTaxExpense",
        "netIncome",
        "changeInCashAndCashEquivalents",
        "totalLiabilities",
        "totalNonCurrentAssets",
        "symbol",
        "sharePrice",
        "1y_sharePrice",
        "cashAndCashEquivalentsAtCarryingValue",
        "propertyPlantEquipment",
        "sector",
        "P/E",
        "ROE",
        "ROA",
        "bookValue",
        "meanSectorPrice",
    ]
    # Verificar que los datos procesados cumplen con los requisitos necesarios para el modelo
    for attribute in attributes_required:
        assert attribute in data_manager.preprocessed_data.columns


def test_prediccion_precios_acciones(data_manager):
    """
    Test ID: TU-DM-03
    Requisito cubierto: RF-03: Predicción de precios de acciones

    Este test verifica que el sistema pueda realizar predicciones del precio de la acción
    para el próximo año, utilizando datos históricos. Se espera que el modelo de predicción
    utilice correctamente estos datos para ofrecer estimaciones confiables.

    Metodología: Se ejecuta la función make_predictions() del data_manager, la cual debe
    utilizar los datos financieros procesados para generar predicciones de precios.

    Salida esperada: La función debe devolver una lista de predicciones, donde cada predicción
    representa la estimación del precio de la acción para un futuro próximo, validando así la
    capacidad predictiva del sistema.
    """
    # Verificar que se devuelve una lista de predicciones y no está vacía
    assert isinstance(data_manager.predictions, list), "La salida debe ser una lista"
    assert (
        len(data_manager.predictions) > 0
    ), "La lista de predicciones no debe estar vacía"
    assert all(
        isinstance(pred, (int, float)) for pred in data_manager.predictions
    ), "Todas las predicciones deben ser números"


def test_generacion_calificaciones_empresas(data_manager):
    """
    Test ID: TU-DM-04
    Requisito cubierto: RF-04: Generación de calificaciones de empresas

    Este test verifica que el sistema pueda asignar calificaciones adecuadas
    a empresas basándose en las predicciones del margen de beneficio.

    Metodología: Se ejecuta la función calculate_rating() del data_manager,
    utilizando las predicciones realizadas y los datos financieros descargados.
    Y se comprobará la devolución del diccionario esperado.

    Salida esperada: La función debe devolver la calificación y los ratios
    empleados en su cálculo.
    """
    validate_payload(data_manager.ratings, "schema_ratings.json")


def test_preparar_respuesta(data_manager):
    """
    Test ID: TU-DM-05
    Requisito cubierto: RF-05: Generación de la respuesta del backend

    Este test verifica que el sistema puede tomar los datos financieros,
    predicciones y calificación y con ello formar la respuesta que se
    mandará al cliente.

    Metodología: Se ejecuta la función prepare_response() del data_manager,
    la cual debe combinar todos los datos necesarios en la estructura de
    respuesta final.

    Salida esperada: La función debe devolver un diccionario que contiene todas las partes
    necesarias, asegurando que todos los elementos requeridos estén presentes y
    correctamente formateados.
    """
    response = data_manager.prepare_response()
    validate_payload(response, "schema_response.json")
