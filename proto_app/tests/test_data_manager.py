"""
Bateria de pruebas para el modulo de data_manager del backend
"""
# pylint: disable=C0413,E0401,E0402,W0621
from data_manager import DataManager
import pytest

@pytest.fixture
def data_manager():
    """Fixture de pytest para crear una instancia de DataManager."""
    dm = DataManager(ticker="AAPL")
    return dm


def test_recoleccion_datos_historicos(data_manager):
    """
    Test para verificar que la recolección de datos históricos de acciones
    se realiza correctamente. Este test simula la respuesta de la descarga de datos.
    """
    financial_data_attributes: tuple = (
        "TIME_SERIES_MONTHLY_ADJUSTED",
        "INCOME_STATEMENT",
        "BALANCE_SHEET",
        "CASH_FLOW",
        "OVERVIEW",
    )

    # Ejecutar la función de descarga de datos
    result = data_manager.download_financial_data()

    # Verificar que los datos se han recolectado correctamente
    for attribute in financial_data_attributes:
        assert attribute in result
