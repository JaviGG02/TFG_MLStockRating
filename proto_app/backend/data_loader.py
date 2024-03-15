# Api
import json
import requests
# Gestion de los datos
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta


# Obtenemos la clave para la api
with open(r"C:\Users\xavic\Escritorio\TFG_MLStockRating\proto_app\backend\config.json", 'r') as file:
    config = json.load(file)
alphavantage_key = config["Alphavantage_key"]

# Funciones auxiliares
def download_financial_data(ticker: str):
    """
    Funcion para la obtencion del historial de precios y los funadamentales de una empresaa
    :ticker: string con el ticker de la empresa
    """
    print(f"Obteniendo los datos de {ticker}")

    result = {}

    # Obtención de fundamentales y precios
    for element in ["TIME_SERIES_MONTHLY_ADJUSTED", "INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW", "OVERVIEW"]:
        print(f"{element} descargado")
        url = f'https://www.alphavantage.co/query?function={element}&symbol={ticker}&apikey={alphavantage_key}'
        r = requests.get(url)
        fundamentals = r.json()
        if not fundamentals:
            return KeyError(f"Información sobre {ticker} no disponible")
        # Caso de superar el limite de acccesos por minuto de la API 
        while 'Note' in fundamentals:
            print("Waiting for 20 seconds for AlphaVantage API limit!")
            time.sleep(20)
            r = requests.get(url)
            fundamentals = r.json()
        result[element] = fundamentals

    return result

def closest_price_from_df(fecha_objetivo: pd.Timestamp, df_prices: pd.DataFrame):
    """
    Funcion para obtener la fila del dataframe de precios con la fecha mas cercana al dia indicado
    """
    # Calcular la diferencia absoluta entre la fecha objetivo y todas las fechas en el indice
    diferencias = abs(df_prices.index - fecha_objetivo)
    # Encuentra la fecha con la diferencia minima, menor a 40 dias
    fecha_mas_cercana = df_prices.index[diferencias.argmin()]
    if abs(fecha_objetivo-fecha_mas_cercana) > pd.Timedelta(days=40):
        return pd.Series() # Devolvemos None
    return df_prices.loc[fecha_mas_cercana]

def preprocess_financial_data(financials: dict):
    """
    Función para el preprocesamiento, preparación y limpieza de los datos financieros. Devuelve un dataframe con toda la información necesaria para pasarsela al modelo
    :financials: Diccionario con las siguientes calves: TIME_SERIES_MONTHLY_ADJUSTED, INCOME_STAMENT, BALANCE_SHEET, CASH_FLOW y OVERVIEW
    """    
    print("Preparando los datos para ingestión del modelo")

    # Crear un DataFrame a partir de los datos financieros
    fundamentals = None
    for element in ["INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"]:
        # Convertimos los datos de cada elemento a df
        element_df = pd.DataFrame(financials[element]["quarterlyReports"])
        element_df.sort_values(by='fiscalDateEnding', inplace=True)
        element_df.reset_index(drop=True, inplace=True)
        # Añadimos al df final de resultados
        if fundamentals is None: fundamentals = element_df
        else: fundamentals = pd.merge(fundamentals, element_df, on='fiscalDateEnding', how='left', suffixes=('', '_drop'))
    drop_cols = [col for col in fundamentals.columns if col.endswith('_drop')]
    fundamentals = fundamentals.drop(columns=drop_cols)
    fundamentals = fundamentals.apply(pd.to_numeric, errors='ignore')

    # Almacenamiento del cierre del precio ajustado en base a fechas
    adjusted_close = {date: values['5. adjusted close'] for date, values in financials['TIME_SERIES_MONTHLY_ADJUSTED']['Monthly Adjusted Time Series'].items()}
    diccionario_precios = {'TIME_SERIES_MONTHLY_ADJUSTED': adjusted_close}
    prices_df = pd.DataFrame.from_dict(diccionario_precios, orient='columns')

    prices_df.index = pd.to_datetime(prices_df.index)
    fundamentals['fiscalDateEnding'] = pd.to_datetime(fundamentals['fiscalDateEnding'])
    fundamentals['sharePrice'] = fundamentals['fiscalDateEnding'].apply(lambda date: closest_price_from_df(date, prices_df))
    fundamentals['1y_sharePrice'] = fundamentals['fiscalDateEnding'].apply(lambda date: closest_price_from_df(date + timedelta(days=365), prices_df))
    fundamentals['sharePrice'], fundamentals['1y_sharePrice'] = pd.to_numeric(fundamentals['sharePrice']), pd.to_numeric(fundamentals['1y_sharePrice'])

    # Calculos de los ratios necesarios para los modelos
    # EPS
    fundamentals['EPS'] = fundamentals['netIncome'] / fundamentals['commonStock']
    # P/E
    fundamentals['P/E'] = fundamentals['sharePrice'] / fundamentals['EPS']
    # ROE
    fundamentals['ROE'] = fundamentals['netIncome'] / fundamentals['totalShareholderEquity']
    # ROA
    fundamentals['ROA'] = fundamentals['netIncome'] / fundamentals['totalAssets']
    # Calculo del book value para evaluacion del precio
    fundamentals['bookValue'] = (fundamentals['totalAssets'] - fundamentals['totalLiabilities']) / fundamentals['commonStock']
    
    # Añadimos el sector y simbolo de la empresa
    fundamentals['sector'] = financials['OVERVIEW']['Sector']
    fundamentals['symbol'] = financials['OVERVIEW']['Symbol']

    # Computar media del sector anual
    fundamentals['fiscalDateEnding'] = pd.to_datetime(fundamentals['fiscalDateEnding'])
    fundamentals['year'] = fundamentals['fiscalDateEnding'].dt.year

    mean_price_by_sector_year = fundamentals.groupby(['sector', 'year'])['sharePrice'].mean().reset_index(name='meanSectorPrice')
    fundamentals = fundamentals.merge(mean_price_by_sector_year, on=['sector', 'year'])

    # Nos quedamos con las columnas que nos interesen
    columns_required = ['fiscalDateEnding', 'totalAssets', 'commonStock', 'retainedEarnings',
       'totalShareholderEquity', 'incomeTaxExpense', 'netIncome',
       'changeInCashAndCashEquivalents', 'totalLiabilities',
       'totalNonCurrentAssets', 'symbol', 'sharePrice', '1y_sharePrice',
       'cashAndCashEquivalentsAtCarryingValue', 'propertyPlantEquipment',
       'sector', 'P/E', 'ROE', 'ROA', 'bookValue', 'meanSectorPrice']
    ml_data = fundamentals.reindex(columns=columns_required)
    ml_data.replace(to_replace=[np.inf, -np.inf, "None"], value=np.nan, inplace=True)

    return ml_data
