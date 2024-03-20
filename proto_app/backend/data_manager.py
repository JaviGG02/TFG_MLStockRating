# Api
import json
import requests
# Dataclass
from dataclasses import dataclass, field
from typing import Union
# Gestion de los datos
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime, timedelta
# Gestion del __o y predicciones
from joblib      import load
from datetime    import datetime, timedelta

@dataclass
class DataManager:
    """
    Clase para la gestion de la descarga, procesamiento y utilización de los datos financieros, así como la preparación de la respuesta
    :ticker: este parametro es una string con el que buscaremos los datos financieros referentes a una empresa
    """

    # Definicion de variables de entrada
    ticker: str

    # Variables privadas
    _respuesta: dict = field(default_factory=dict)

    __financial_data: dict = field(default_factory=dict)
    __calification_data: int = field(default_factory=int)
    __predictions_data: dict = field(default_factory=dict)
    __ml_data: pd.DataFrame = field(default_factory=pd.DataFrame)
    __prices_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    __predictions: list = field(default_factory=list)
    

    # Gestion de constantes
    __FINANCIAL_DATA_ATTRIBUTES: tuple = ("TIME_SERIES_MONTHLY_ADJUSTED", "INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW", "OVERVIEW")
    __FUNDAMENTAL_ATTRIBUTES: tuple = ("INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW")
    with open(r"C:\Users\xavic\Escritorio\TFG_MLStockRating\proto_app\backend\config.json", 'r') as file: config = json.load(file)
    __ALPHA_VANTAGE_KEY = config["Alphavantage_key"]
    __MODEL = load(r'C:\Users\xavic\Escritorio\TFG_MLStockRating\proto_app\backend\gb_model.joblib')

    # Metodos Auxiliares
    def closest_price_from_df(self, fecha_objetivo: pd.Timestamp) -> Union[pd.Series | pd.DataFrame] :
        """
        Metodo para obtener la fila del dataframe de precios con la fecha mas cercana al dia indicado.
        Devuelve la linea de __prices_df con el precio mas cercano a la fecha objetivo en caso de haberlo encontrado, 
        si no, devuelve una np.Series vacia
        """
        # Calcular la diferencia absoluta entre la fecha objetivo y todas las fechas en el indice
        diferencias = abs(self.__prices_df.index - fecha_objetivo)
        # Encuentra la fecha con la diferencia minima, menor a 40 dias
        fecha_mas_cercana = self.__prices_df.index[diferencias.argmin()]

        if abs(fecha_objetivo-fecha_mas_cercana) > pd.Timedelta(days=40):
            return pd.Series() # Devolvemos None
        return self.__prices_df.loc[fecha_mas_cercana]
    
    def replace_values_in_nested_dict(self, d: dict, old_values: list, new_value: str) -> dict:
        """
        Metodo recursiva para quitar valores no deseados en un diccionario. Devuelve el diccionario cambiado.
        :d: Diccionario a tratar.
        :old_values: lista de valores a cambiar.
        :new_value: valor de cambio.
        """
        for k, v in d.items():
            if isinstance(v, dict):
                d[k] = self.replace_values_in_nested_dict(v, old_values, new_value)
            elif str(v) in old_values: 
                d[k] = new_value
        return d

    # Metodos principales
    def download_financial_data(self) -> dict:
        """
        Metodo para la obtencion del historial de precios y los fundamentales de una empresa. Devuelve el diccionario con 
        toda la informacion descargada, y en caso de que no encuentre el simbolo, devuelve KeyError.
        """
        print(f"Obteniendo los datos de {self.ticker}")

        # Obtención de fundamentales y precios
        for element in self.__FINANCIAL_DATA_ATTRIBUTES:
            print(f"{element} descargado")
            url = f'https://www.alphavantage.co/query?function={element}&symbol={self.ticker}&apikey={self.__ALPHA_VANTAGE_KEY}'
            r = requests.get(url)
            downloaded = r.json()
            if not downloaded:
                print(f"Información sobre {self.ticker} no disponible")
                self.__financial_data = {"Error":f"Información sobre {self.ticker} no disponible"}
                break
            # Caso de superar el limite de acccesos por minuto de la API 
            while 'Note' in downloaded:
                print("Waiting for 20 seconds for AlphaVantage API limit!")
                time.sleep(20)
                r = requests.get(url)
                downloaded = r.json()

            self.__financial_data[element] = downloaded

        return self.__financial_data

    
    def preprocess_financial_data(self) ->  pd.DataFrame:
        """
        Metodo para el preprocesamiento, preparación y limpieza de los datos financieros. Devuelve un dataframe con toda la información 
        necesaria para pasarsela al __o.
        """    
        print("Preparando los datos para ingestión del modelo")

        # Crear un DataFrame a partir de los datos financieros
        financial_df = None
        for element in self.__FUNDAMENTAL_ATTRIBUTES:
            # Convertimos los datos de cada elemento a df
            element_df = pd.DataFrame(self.__financial_data[element]["quarterlyReports"])
            element_df.sort_values(by='fiscalDateEnding', inplace=True)
            element_df.reset_index(drop=True, inplace=True)
            # Añadimos al df final de resultados
            if financial_df is None: financial_df = element_df
            else: financial_df = pd.merge(financial_df, element_df, on='fiscalDateEnding', how='left', suffixes=('', '_drop'))
        drop_cols = [col for col in financial_df.columns if col.endswith('_drop')]
        financial_df = financial_df.drop(columns=drop_cols)
        financial_df = financial_df.apply(pd.to_numeric, errors='ignore')

        # Gestion de los precios: __prices_df
        adjusted_close = {date: values['5. adjusted close'] for date, values in 
                          self.__financial_data['TIME_SERIES_MONTHLY_ADJUSTED']['Monthly Adjusted Time Series'].items()}
        prices_dict = {'TIME_SERIES_MONTHLY_ADJUSTED': adjusted_close}
        self.__prices_df = pd.DataFrame.from_dict(prices_dict, orient='columns')

        # Gestion de los precios: financial_df
        self.__prices_df.index = pd.to_datetime(self.__prices_df.index)
        financial_df['fiscalDateEnding'] = pd.to_datetime(financial_df['fiscalDateEnding'])
        financial_df['sharePrice'] = financial_df['fiscalDateEnding'].apply(lambda date:self.closest_price_from_df(date))
        financial_df['1y_sharePrice'] = financial_df['fiscalDateEnding'].apply(lambda date:self.closest_price_from_df(date + timedelta(days=365)))
        financial_df['sharePrice'] = pd.to_numeric(financial_df['sharePrice'])
        financial_df['1y_sharePrice'] = pd.to_numeric(financial_df['1y_sharePrice'])

        # Calculos de los ratios necesarios para los __os
        # EPS
        financial_df['EPS'] = financial_df['netIncome'] / financial_df['commonStock']
        # P/E
        financial_df['P/E'] = financial_df['sharePrice'] / financial_df['EPS']
        # ROE
        financial_df['ROE'] = financial_df['netIncome'] / financial_df['totalShareholderEquity']
        # ROA
        financial_df['ROA'] = financial_df['netIncome'] / financial_df['totalAssets']
        # Book Value
        financial_df['bookValue'] = (financial_df['totalAssets'] - financial_df['totalLiabilities']) / financial_df['commonStock']
        
        # Sector y simbolo
        financial_df['sector'] = self.__financial_data['OVERVIEW']['Sector']
        financial_df['symbol'] = self.__financial_data['OVERVIEW']['Symbol']

        # Media del sector anual
        financial_df['fiscalDateEnding'] = pd.to_datetime(financial_df['fiscalDateEnding'])
        financial_df['year'] = financial_df['fiscalDateEnding'].dt.year

        mean_price_by_sector_year = financial_df.groupby(['sector', 'year'])['sharePrice'].mean().reset_index(name='meanSectorPrice')
        financial_df = financial_df.merge(mean_price_by_sector_year, on=['sector', 'year'])

        # Nos quedamos con las columnas con las que fue entrenado el __o
        columns_required = [
            'fiscalDateEnding', 'totalAssets', 'commonStock', 'retainedEarnings',
            'totalShareholderEquity', 'incomeTaxExpense', 'netIncome',
            'changeInCashAndCashEquivalents', 'totalLiabilities',
            'totalNonCurrentAssets', 'symbol', 'sharePrice', '1y_sharePrice',
            'cashAndCashEquivalentsAtCarryingValue', 'propertyPlantEquipment',
            'sector', 'P/E', 'ROE', 'ROA', 'bookValue', 'meanSectorPrice'
        ]
        self.__ml_data = financial_df.reindex(columns=columns_required)
        self.__ml_data.replace(to_replace=[np.inf, -np.inf, "None"], value=np.nan, inplace=True)

        # Eliminamos aquellas filas que no tengan información sobre 1y_sharePrice y sean anteriores al dia actual
        current_date = datetime.now()
        mask = self.__ml_data['1y_sharePrice'].notna() | (self.__ml_data['fiscalDateEnding'] >= current_date)
        self.__ml_data = self.__ml_data[mask].reset_index(drop=True)

        return self.__ml_data
    
    
    def make_predictions(self) -> Union[list, int]:
        """
        Metodo que toma los datos financieros procesados (_) para hacer las predicciones y aportar una calificacion 
        en base al retorno esperado. Devuelve una lista de predicciones realizadas y un numero entero que representa la calificación otorgada
        """
        print(f"Realizando predicciones")
        
        for i in range(len(self.__ml_data)):    
            temp_model = self.__MODEL # Modelo temporal para entrenamiento
            if not np.isnan(self.__ml_data.iloc[i]['1y_sharePrice']):
                # Entrenamiento
                y_train = self.__ml_data.iloc[:i+1]['1y_sharePrice']
                X_train = self.__ml_data.iloc[:i+1].drop(['1y_sharePrice'], axis=1)
                temp_model.fit(X_train, y_train)
                # Prediccion
                try:
                    X_next = self.__ml_data.iloc[[i+1]].drop(['1y_sharePrice'], axis=1)
                except IndexError:
                    return self.__predictions, -1
                y_pred = temp_model.predict(X_next) 
                self.__predictions.append(float(y_pred.item()))
            else:
                # Prediccion final
                X_next = self._.iloc[i:].drop(['1y_sharePrice'], axis=1)
                self.__MODEL.fit(X_train, y_train)
                y_pred = self.__MODEL.predict(X_next) 
                for pred in list(y_pred):
                    self.__predictions.append(float(pred.item()))
                break
        
        # Generacion de la calificacion
        pct_return = (self.__predictions[-1] - self.__ml_data["sharePrice"].iloc[-1]) / self.__predictions[-1]
        if pct_return < -5:
            self._calification = 1
        elif pct_return < 0:
            self._calification = 2
        elif pct_return < 5:
            self._calification = 3
        elif pct_return < 10:
            self._calification = 4;
        else:
            self._calification = 5

        return self.__predictions, self._calification
    
    def prepare_response(self) -> dict:
        """
        Metodo para la preparación de la respuesta. Toma como los datos del dataframe de datos financieros y los transforma a diccionarios.
        Finalmente, junta toda la informacion y devuelve el diccionario de la respuesta
        """
        # Obtencion del diccionario de _predictions 
        predictions_df = pd.DataFrame(self.__predictions, columns=['predicted_1y_sharePrice'])
        predictions_df['fiscalDateEnding'] = self.__ml_data['fiscalDateEnding'] + timedelta(days=365)
        predictions_df['fiscalDateEnding'] = predictions_df['fiscalDateEnding'].dt.strftime('%Y-%m')
        self.__predictions_data = dict(zip(predictions_df['fiscalDateEnding'], predictions_df['predicted_1y_sharePrice']))

        # Obtencion del diccionario de TIME_SERIES_MONTHLY_ADJUSTED -> finalizacion del diccionario de __financial_data
        self.__ml_data['fiscalDateEnding'] = self.__ml_data['fiscalDateEnding'].dt.strftime('%Y-%m')
        del self.__financial_data['TIME_SERIES_MONTHLY_ADJUSTED']
        self.__financial_data['TIME_SERIES_MONTHLY_ADJUSTED'] = dict(zip(self.__ml_data['fiscalDateEnding'], self.__ml_data['sharePrice']))

        # Rellenamos los días de predicciones de los cuales tenemos datos de precios (caso de desfase por publicacion de resultados)
        for fecha in predictions_df['fiscalDateEnding']:
            if fecha not in self.__ml_data['fiscalDateEnding'].values:
                fecha_objetivo = pd.to_datetime(fecha, format='%Y-%m')
                closest_price = self.closest_price_from_df(fecha_objetivo)
                self.__financial_data['TIME_SERIES_MONTHLY_ADJUSTED'][fecha] = closest_price.values[0]

        self.__financial_data['TIME_SERIES_MONTHLY_ADJUSTED'] = self.replace_values_in_nested_dict(
            self.__financial_data['TIME_SERIES_MONTHLY_ADJUSTED'], ['nan', 'NaN', 'N/A'], "None"
        )

        # Preparar la respuesta
        self._respuesta = {
            'datos_financieros': self.__financial_data,
            'prediccion': self.__predictions_data,
            'calificacion': self.__calification_data
        }

        return self._respuesta