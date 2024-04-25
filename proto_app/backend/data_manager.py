"""
Modulo encargado de la gestion de la clase DataManager
"""

# pylint: disable=E0401
from dataclasses import dataclass, field
from typing import Union
from datetime import datetime, timedelta
import json
import os
import time
from pathlib import Path
import requests
import pandas as pd
import numpy as np
from joblib import load
from data_manager_aux import (
    closest_price_from_df,
    replace_values_in_nested_dict,
    ratio_calculation,
    geometric_mean_growth_rate,
    score_for_ratio,
)


# Gestion de constantes y modelo
FINANCIAL_DATA_ATTRIBUTES: tuple = (
    "TIME_SERIES_MONTHLY_ADJUSTED",
    "INCOME_STATEMENT",
    "BALANCE_SHEET",
    "CASH_FLOW",
    "OVERVIEW",
)
FUNDAMENTAL_ATTRIBUTES: tuple = ("INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW")
CONFIG_PATH = str(Path(__file__).resolve().parents[0]) + "/config.json"
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = json.load(file)
else:
    api_key = os.getenv("API_KEY")
    config = {"Alphavantage_key": api_key}
# Modelo ML
MODEL_PATH = str(Path(__file__).resolve().parents[0]) + "/gb_model.joblib"
model = load(MODEL_PATH)


@dataclass
class DataManager:
    """
    Clase para la gestion de la descarga, procesamiento y utilización de los datos financieros,
    así como la preparación de la respuesta.
    :ticker: este parametro es una string con el que buscaremos los datos financieros
    referentes a una empresa
    """

    # Variables de entrada
    ticker: str

    # Diccionario donde se almacenara toda la informacion de la respuesta
    respuesta: dict = field(default_factory=dict)
    # Diccionario con fundamentales, precios y overview
    __financial_data: dict = field(default_factory=dict)
    # Diccionario con los resultados del estudio financiero y calificacion
    __calification_data: int = field(default_factory=dict)
    # Diccionario de predicciones realizadas por el modelo
    __predictions_data: dict = field(default_factory=dict)
    # Dataframe con datos cuatrimestrales fundamentales
    __financial_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    # Dataframe con la informacion para pasar al modelo creado a partir de self.__financial_df
    __ml_data: pd.DataFrame = field(default_factory=pd.DataFrame)
    # Daraframe de precios
    __prices_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    # Lista de predicciones para formar __predictions_data
    __predictions: list = field(default_factory=list)
    # Clave de acceso API
    __alpha_vantage_key = config["Alphavantage_key"]

    # Metodos principales

    def download_financial_data(self) -> dict:
        """
        Metodo para la obtencion del historial de precios y los fundamentales de una empresa.
        Devuelve el diccionario con toda la informacion descargada, y en caso de que no
        encuentre el simbolo, devuelve KeyError.
        """

        print(f"Obteniendo los datos de {self.ticker}")
        # Obtención de fundamentales y precios
        try:
            for element in FINANCIAL_DATA_ATTRIBUTES:
                print(f"{element} descargado")
                url = f"https://www.alphavantage.co/query?function={element}&symbol={self.ticker}&apikey={self.__alpha_vantage_key}"  # pylint: disable=C0301
                r = requests.get(url, timeout=1000)
                downloaded = r.json()
                if not downloaded:
                    print(f"Información sobre {self.ticker} no disponible")
                    self.__financial_data = {
                        "Error": f"Información sobre {self.ticker} no disponible"
                    }
                    break
                # Caso de superar el limite de acccesos por minuto de la API
                while "Note" in downloaded:
                    print("Waiting for 20 seconds for AlphaVantage API limit!")
                    time.sleep(20)
                    r = requests.get(url, timeout=1000)
                    downloaded = r.json()

                self.__financial_data[element] = downloaded

        except requests.exceptions.JSONDecodeError:
            self.__financial_data = {
                "Error": f"Información sobre {self.ticker} no disponible"
            }
        return self.__financial_data

    def preprocess_financial_data(self) -> pd.DataFrame:
        """
        Metodo para el preprocesamiento, preparación y limpieza de los datos financieros.
        Devuelve un dataframe con toda la información necesaria para pasarsela al modelo.
        """
        print("Preparando los datos para ingestión del modelo")

        # Crear un DataFrame a partir de los datos financieros
        self.__financial_df = None
        for element in FUNDAMENTAL_ATTRIBUTES:
            # Convertimos los datos de cada elemento a df
            element_df = pd.DataFrame(
                self.__financial_data[element]["quarterlyReports"]
            )
            element_df.sort_values(by="fiscalDateEnding", inplace=True)
            element_df.reset_index(drop=True, inplace=True)
            # Añadimos al df final de resultados
            if self.__financial_df is None:
                self.__financial_df = element_df
            else:
                self.__financial_df = pd.merge(
                    self.__financial_df,
                    element_df,
                    on="fiscalDateEnding",
                    how="left",
                    suffixes=("", "_drop"),
                )
        drop_cols = [
            col for col in self.__financial_df.columns if col.endswith("_drop")
        ]
        self.__financial_df = self.__financial_df.drop(columns=drop_cols)
        self.__financial_df = self.__financial_df.apply(pd.to_numeric, errors="ignore")

        # Gestion de los precios: __prices_df
        adjusted_close = {
            date: values["5. adjusted close"]
            for date, values in self.__financial_data["TIME_SERIES_MONTHLY_ADJUSTED"][
                "Monthly Adjusted Time Series"
            ].items()
        }
        prices_dict = {"TIME_SERIES_MONTHLY_ADJUSTED": adjusted_close}
        self.__prices_df = pd.DataFrame.from_dict(prices_dict, orient="columns")

        # Gestion de los precios: __financial_df
        self.__prices_df.index = pd.to_datetime(self.__prices_df.index)
        self.__financial_df["fiscalDateEnding"] = pd.to_datetime(
            self.__financial_df["fiscalDateEnding"]
        )
        self.__financial_df["sharePrice"] = self.__financial_df[
            "fiscalDateEnding"
        ].apply(
            lambda date: closest_price_from_df(
                prices_df=self.__prices_df, fecha_objetivo=date
            )
        )
        self.__financial_df["1y_sharePrice"] = self.__financial_df[
            "fiscalDateEnding"
        ].apply(
            lambda date: closest_price_from_df(
                prices_df=self.__prices_df, fecha_objetivo=date + timedelta(days=365)
            )
        )
        self.__financial_df = self.__financial_df.apply(pd.to_numeric, errors="ignore")
        # Calculos de los ratios necesarios
        self.__financial_df["EPS"] = self.__financial_df.apply(
            lambda row: ratio_calculation(
                operation=lambda: row["netIncome"] / row["commonStock"], default=np.nan
            ),
            axis=1,
        )
        self.__financial_df["P/E"] = self.__financial_df.apply(
            lambda row: ratio_calculation(
                operation=lambda: row["sharePrice"] / row["EPS"], default=np.nan
            ),
            axis=1,
        )
        self.__financial_df["ROE"] = self.__financial_df.apply(
            lambda row: ratio_calculation(
                operation=lambda: row["netIncome"] / row["totalShareholderEquity"],
                default=np.nan,
            ),
            axis=1,
        )
        self.__financial_df["ROA"] = self.__financial_df.apply(
            lambda row: ratio_calculation(
                operation=lambda: row["netIncome"] / row["totalAssets"], default=np.nan
            ),
            axis=1,
        )
        self.__financial_df["bookValue"] = self.__financial_df.apply(
            lambda row: ratio_calculation(
                operation=lambda: (row["totalAssets"] - row["totalLiabilities"])
                / row["commonStockSharesOutstanding"],
                default=np.nan,
            ),
            axis=1,
        )
        self.__financial_df["currentRatio"] = self.__financial_df.apply(
            lambda row: ratio_calculation(
                operation=lambda: (row["totalCurrentAssets"])
                / row["totalCurrentLiabilities"],
                default=np.nan,
            ),
            axis=1,
        )
        self.__financial_df["debtEquityRatio"] = self.__financial_df.apply(
            lambda row: ratio_calculation(
                operation=lambda: (row["totalLiabilities"])
                / row["totalShareholderEquity"],
                default=np.nan,
            ),
            axis=1,
        )
        self.__financial_df["freeCashFlow"] = self.__financial_df.apply(
            lambda row: ratio_calculation(
                operation=lambda: (row["operatingCashflow"])
                - row["capitalExpenditures"],
                default=np.nan,
            ),
            axis=1,
        )
        # Sector y simbolo
        self.__financial_df["sector"] = self.__financial_data["OVERVIEW"]["Sector"]
        self.__financial_df["symbol"] = self.__financial_data["OVERVIEW"]["Symbol"]

        # Media del sector anual
        self.__financial_df["fiscalDateEnding"] = pd.to_datetime(
            self.__financial_df["fiscalDateEnding"]
        )
        self.__financial_df["year"] = self.__financial_df["fiscalDateEnding"].dt.year

        mean_price_by_sector_year = (
            self.__financial_df.groupby(["sector", "year"])["sharePrice"]
            .mean()
            .reset_index(name="meanSectorPrice")
        )
        self.__financial_df = self.__financial_df.merge(
            mean_price_by_sector_year, on=["sector", "year"]
        )

        # Nos quedamos con las columnas con las que fue entrenado el modelo
        columns_required = [
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
        self.__ml_data = self.__financial_df.reindex(columns=columns_required)
        self.__ml_data.replace(
            to_replace=[np.inf, -np.inf, "None"], value=np.nan, inplace=True
        )

        # Eliminamos aquellas filas que no tengan información sobre 1y_sharePrice y
        # sean anteriores al dia actual
        current_date = datetime.now() - timedelta(days=365)
        mask = self.__ml_data["1y_sharePrice"].notna() | (
            self.__ml_data["fiscalDateEnding"] >= current_date
        )
        self.__ml_data = self.__ml_data[mask].reset_index(drop=True)

        return self.__ml_data

    def make_predictions(self) -> Union[list, int]:
        # pylint: disable=C0103
        """
        Metodo que toma los datos financieros procesados para hacer las predicciones.
        Devuelve una lista de predicciones realizadas.
        """
        print("Realizando predicciones")
        for i in range(len(self.__ml_data)):
            temp_model = model  # Modelo temporal para entrenamiento
            if not np.isnan(self.__ml_data.iloc[i]["1y_sharePrice"]):
                # Entrenamiento
                y_train = self.__ml_data.iloc[: i + 1]["1y_sharePrice"]
                X_train = self.__ml_data.iloc[: i + 1].drop(["1y_sharePrice"], axis=1)
                temp_model.fit(X_train, y_train)
                # Prediccion
                try:
                    X_next = self.__ml_data.iloc[[i + 1]].drop(
                        ["1y_sharePrice"], axis=1
                    )
                except IndexError:
                    return self.__predictions, -1
                y_pred = temp_model.predict(X_next)
                self.__predictions.append(float(y_pred.item()))
            else:
                # Prediccion final
                X_next = self.__ml_data.iloc[i:].drop(["1y_sharePrice"], axis=1)
                model.fit(X_train, y_train)
                y_pred = model.predict(X_next)
                for pred in list(y_pred):
                    self.__predictions.append(float(pred.item()))
                break

        return self.__predictions

    def calculate_rating(self):
        # pylint: disable = C0301
        """
        Metodo para el calculo del rating en base al retorno de precio esperado y tres factores financieros.
        Las reglas para el calculo son las siguientes:
            1) Rate = pricePredictionReturn * norm_f + GPH;
                1.1) pricePredictionReturn: retorno porcentual de la acción en función del último data point predicho
                1.2) Norm_f: factor normalizador que toma en cuenta el precio más alto que ha tenido la accion para evitar una gran variabilidad en casos de bajo precio,
                             como podría ser "meme" stocks
                1.3) GPH: factor que se computa sumando todas las componentes expuestas anteriormente
            2) Componentes GPH: cada componente tiene el mismo peso, sin embargo, los pesos de los atributos de cada componente varían en función del numero de atributos en el componente
                - Crecimiento (G): tasa de crecimiento medio geometrico de ganancias, ebitda, cash flows y dividendos
                - Rentabilidad (P): tasa de crecimiento medio geometrico de ganancias netas y scores de ratios: ROE, ROA y sharePrice/bookValue
                - Salud Financiera (H): scores de ratios: current y D/E
                2.1) Ratios: definidos sus thresholds en ratio-values, siguen las siguientes restricciones:
                    2.1.1) Valores entre -100 y 100 (exceptuando bookValue/sharePrice que puede tomar valores más bajos de -100, para influir en la nota final).
                    2.1.2) En caso de sobrepasar el threshold del ratio (la marca considerada usualmente como buen indicador) se asigna el máximo valor
                    2.1.3) En caso de tener un ratio por debajo de un valor de -3, lo penalizamos con un factor x10
                    2.1.4) En caso de que el ratio no llegue al threshold se computara su valor en función de la distancia al mismo
                2.2) Book Value: el book value lo utilizamos como medida para saber si una acción está sobre/infra-valorada. Para ello lo transformamos
                                 en un ratio, la inversa de "Price-to-Book Value". Por tanto, se le aplican las mismas reglas que a otros ratios.
                2.3) Otros fundamentales: para saber si una empresa ha conseguido generar (o no) beneficios en los últimos años debemos utilizar GMGR
                                 (Geometric Mean Growth Rate), con este algoritmo tomaremos el productorio de todos los valores de crecimiento y haremos
                                 su raiz n-esima en funcion de los periodos. De esta manera tenemos en cuenta todos los periodos y su crecimiento (o
                                 decrecimiento). Las restricciones que aplican a estos valores:
                    2.3.1) Sus valores estaran entre -100 y 100.
                    2.3.2) En caso de factores geometricos negativos (>-1) no se tomara en cuenta ese periodo
                    2.3.3) Debido a que los valores de GMGR suelen ser "bajos" en la escala 0-100 (por ejemplo, es muy raro que el beneficio neto suba
                            un 50% o más de un periodo a otro), por ello, se aplica un factor de amplificación de 10.

        remarks: debemos tener en cuenta que en algunos casos no contamos con los datos fundamentales, en dicho caso el atributo tomara valor de 0
        """

        scores = {
            "growth": {
                "totalRevenue": None,
                "ebitda": None,
                "freeCashFlow": None,
                "dividendPayout": None,
            },
            "profitability": {
                "netIncome": None,
                "ROE": None,
                "ROA": None,
                "bookValue": None,
            },
            "financialHealth": {
                "currentRatio": None,
                "debtEquityRatio": None,
            },
            "pricePredictionReturn": None,
        }

        ratio_values = {
            "ROE": 0.15,
            "ROA": 0.05,
            "currentRatio": 1.0,
            "debtEquityRatio": 1.0,
            "bookValue": 1.0,
        }

        # Normalzacion y calculo de la puntuacion de los atributos
        category_scores = []
        for category, category_item in scores.items():
            # Calculo del rating del precio
            if category == "pricePredictionReturn":
                price_return = (
                    (self.__predictions[-1] - self.__ml_data["sharePrice"].iloc[-1])
                    / self.__predictions[-1]
                ) * 100
                scores["pricePredictionReturn"] = max(price_return, 0)
            # Calculo rating de crecimiento, rentabilidad y salud financiera
            else:
                attribute_scores = []
                for attribute, attribute_item in category_item.items():
                    # Ratios
                    if attribute in ratio_values:
                        attribute_value = self.__financial_df[attribute].iloc[-1]
                        if not np.isnan(attribute_value):
                            # Inversa del Debt To Equity
                            if attribute == "debtEquityRatio":
                                attribute_value = 1 / attribute_value
                            # Inversa del Price To Book Value
                            elif attribute == "bookValue":
                                attribute_value = 1 / (
                                    self.__financial_df["sharePrice"].iloc[-1]
                                    / attribute_value
                                )
                            attribute_item = score_for_ratio(
                                attribute_value, ratio_values[attribute]
                            )
                        else:
                            attribute_item = 0
                    # Otros Fundamentales
                    else:
                        attribute_item = geometric_mean_growth_rate(
                            self.__financial_df, attribute, 5
                        )
                        # Aplicamos factor de amplificacion a gmgr para que tengan peso en la nota
                        attribute_item = min(max(attribute_item * 10, -100), 100)
                    attribute_scores.append(attribute_item)
                    attribute_item = int(attribute_item)
                    scores[category][attribute] = attribute_item
                category_scores.append(sum(attribute_scores) / len(attribute_scores))

        # Calcular la puntuación final, entre 0 y 100
        normilize_factor = (
            self.__ml_data["sharePrice"].iloc[-1] / self.__ml_data["sharePrice"].max()
        )
        scores["finalRate"] = min(
            int(
                scores["pricePredictionReturn"] * normilize_factor
                + (sum(category_scores) / len(category_scores))
            ),
            100,
        )
        if scores["finalRate"] < 0:
            scores["finalRate"] = 0
        self.__calification_data = scores

        return self.__calification_data

    def prepare_response(self) -> dict:
        """
        Metodo para la preparación de la respuesta. Toma como los datos del dataframe de datos
        financieros y los transforma a diccionarios. Finalmente, junta toda la informacion y
        devuelve el diccionario de la respuesta.
        """
        # Obtencion del diccionario de _predictions
        predictions_df = pd.DataFrame(
            self.__predictions, columns=["predicted_1y_sharePrice"]
        )
        predictions_df["fiscalDateEnding"] = self.__ml_data[
            "fiscalDateEnding"
        ] + timedelta(days=365)
        predictions_df["fiscalDateEnding"] = predictions_df[
            "fiscalDateEnding"
        ].dt.strftime("%Y-%m")
        self.__predictions_data = dict(
            zip(
                predictions_df["fiscalDateEnding"],
                predictions_df["predicted_1y_sharePrice"],
            )
        )

        # Obtencion del diccionario de TIME_SERIES_MONTHLY_ADJUSTED -> finalizacion
        # del diccionario de __financial_data
        self.__ml_data["fiscalDateEnding"] = self.__ml_data[
            "fiscalDateEnding"
        ].dt.strftime("%Y-%m")
        del self.__financial_data["TIME_SERIES_MONTHLY_ADJUSTED"]
        self.__financial_data["TIME_SERIES_MONTHLY_ADJUSTED"] = dict(
            zip(self.__ml_data["fiscalDateEnding"], self.__ml_data["sharePrice"])
        )

        self.__financial_data["TIME_SERIES_MONTHLY_ADJUSTED"] = (
            replace_values_in_nested_dict(
                self.__financial_data["TIME_SERIES_MONTHLY_ADJUSTED"],
                ["nan", "NaN", "N/A"],
                "None",
            )
        )

        # Preparar la respuesta
        self.respuesta = {
            "datos_financieros": self.__financial_data,
            "prediccion": self.__predictions_data,
            "calificacion": self.__calification_data,
        }

        return self.respuesta
