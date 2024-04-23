"""
Modulo de python donde se guardan las funciones auxiliares empleadas en data_manager.py
"""

from typing import Union
import pandas as pd
import numpy as np


# Funciones Auxiliares
def closest_price_from_df(
    prices_df: pd.DataFrame, fecha_objetivo: pd.Timestamp
) -> Union[pd.Series | pd.DataFrame]:
    """
    Funcion auxiliar para obtener la fila del dataframe de precios con la fecha mas cercana
    al dia indicado. Devuelve la linea de __prices_df con el precio mas cercano a la fecha
    objetivo en caso de haberlo encontrado, si no, devuelve una np.Series vacia.
    """
    # Calcular la diferencia absoluta entre la fecha objetivo y todas las fechas en el indice
    diferencias = abs(prices_df.index - fecha_objetivo)
    # Encuentra la fecha con la diferencia minima, menor a 40 dias
    fecha_mas_cercana = prices_df.index[diferencias.argmin()]

    if abs(fecha_objetivo - fecha_mas_cercana) > pd.Timedelta(days=40):
        return pd.Series()  # Devolvemos None
    return prices_df.loc[fecha_mas_cercana]


def replace_values_in_nested_dict(d: dict, old_values: list, new_value: str) -> dict:
    """
    Metodo auxiliar recursivo para quitar valores no deseados en un diccionario.
    :d: Diccionario a tratar.
    :old_values: lista de valores a cambiar.
    :new_value: valor de cambio.
    """
    for k, v in d.items():
        if isinstance(v, dict):
            d[k] = replace_values_in_nested_dict(v, old_values, new_value)
        elif str(v) in old_values:
            d[k] = new_value
    return d


def ratio_calculation(operation: callable, default: any = None) -> any:
    """
    Metodo auxiliar que permite el control de las operaciones de ratios
    """
    try:
        return operation()
    except ZeroDivisionError:
        return default


def geometric_mean_growth_rate(data: pd.DataFrame, column: str, y_periods: int = 5):
    """
    Metodo auxiliar para el calculo del crecimiento de la media geometrica, lo que nos permite
    saber si un atributo a crecido o decrecido en el periodo establecido
    """
    filtered_data = pd.to_numeric(data[column].tail(3 * y_periods + 1), errors="ignore")
    if len(filtered_data) < 2:
        return 0
    # Calculo de los crecimientos año a año
    growth_factors = []
    mean_growth_factors = 0
    for i in range(1, len(filtered_data)):
        try:
            growth = (
                filtered_data.iloc[i] - filtered_data.iloc[i - 1]
            ) / filtered_data.iloc[i]
        except TypeError:
            growth = 0
        growth_factors.append(growth)
        mean_growth_factors += abs(growth)
    mean_growth_factors /= len(growth_factors)

    # Calculo de GMGR
    geometric_factors = []
    recorded_periods, skipped_periods = 0, 0
    for g in growth_factors:
        # Excluir crecimientos negativos (resultarían en factores geométricos negativos
        # y numeros complejos) y outliers que sobrepasen excesivamente la media
        # de growth factors
        if g > -1 and abs(g) < abs(mean_growth_factors * 5):
            geometric_factors.append(1 + g)
            recorded_periods += 1
        else:
            skipped_periods += 1

    # Evitar división por cero si la lista está vacía
    if not geometric_factors:
        return 0
    # En caso de no haber el doble de ciclos "positivos" que "negativos" devolvemos 0
    if skipped_periods > 0 and recorded_periods / skipped_periods < 3:
        return 0

    gmgr = np.prod(geometric_factors) ** (1 / len(geometric_factors)) - 1
    return gmgr * 100


def score_for_ratio(attribute_value: float, threshold: float):
    """
    Metodo para asignar una calificacion a un ratio
    """
    # En caso de estar por encima del threshold: maxima nota
    if attribute_value >= threshold:
        return 100
    # En caso de ser negativo: factor de amplificacion, aplicando como limite -100
    if attribute_value < -3:
        return max(10 * attribute_value / threshold, -100)
    # else
    return max(100 * (attribute_value / threshold), -100)
