import requests
import json
import time
import pandas as pd

# Obtenemos la clave de la API de AlphaVantage
with open(f"config.json", "r") as file:
    config = json.load(file)
alphavantage_key = config["Alphavantage_key"]


def obtain_sector_industry(symbol: str):
    """
    Función para la obtención del sector e industria principales donde opera la compañia
    """
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={alphavantage_key}"
    r = requests.get(url)
    data = r.json()
    # Caso de superar el limite de acccesos por minuto de la API
    while "Note" in data:
        print("Waiting for 20 seconds for AlphaVantage API limit!")
        time.sleep(20)
        r = requests.get(url)
        data = r.json()
    try:
        result = (data["Sector"], data["Industry"])
    except KeyError:  # Caso en el que no tenemos la informacion
        result = (pd.NA, pd.NA)
    return result


# Cargamos los datos del CSV con informacion fundamental historica
quarterly_fundamentals = pd.read_csv("data/finnhub_mapped_quarterly.csv", sep=",")

# Agregamos el sector e industria a cada compañia
sectores_industrias = {}
for symbol in quarterly_fundamentals["symbol"].unique():
    print(symbol)
    sectores_industrias[symbol] = obtain_sector_industry(symbol)

quarterly_fundamentals["sector"] = quarterly_fundamentals["symbol"].map(
    lambda symbol: sectores_industrias[symbol][0]
)
quarterly_fundamentals["industria"] = quarterly_fundamentals["symbol"].map(
    lambda symbol: sectores_industrias[symbol][1]
)

print(
    quarterly_fundamentals[quarterly_fundamentals["symbol"] == "AAPL"]["sector"],
    quarterly_fundamentals[quarterly_fundamentals["symbol"] == "AAPL"]["industria"],
)

# Agregamos los calculos de los ratios
# EPS
quarterly_fundamentals["EPS"] = (
    quarterly_fundamentals["netIncome"] / quarterly_fundamentals["commonStock"]
)
# P/E
quarterly_fundamentals["P/E"] = (
    quarterly_fundamentals["sharePrice"] / quarterly_fundamentals["EPS"]
)
# Current Ratio
quarterly_fundamentals["currentRatio"] = (
    quarterly_fundamentals["totalCurrentAssets"]
    / quarterly_fundamentals["totalCurrentLiabilities"]
)
# Inventory Turnover
quarterly_fundamentals["inventoryTurnover"] = (
    quarterly_fundamentals["costofGoodsAndServicesSold"]
    / quarterly_fundamentals["inventory"]
)
# Total Assets Turnover
quarterly_fundamentals["totalAssetsTurnover"] = (
    quarterly_fundamentals["grossProfit"]
    + quarterly_fundamentals["costofGoodsAndServicesSold"]
) / quarterly_fundamentals["totalAssets"]
# Net Margin On Sales
quarterly_fundamentals["totalAssetsTurnover"] = quarterly_fundamentals["netIncome"] / (
    quarterly_fundamentals["grossProfit"]
    + quarterly_fundamentals["costofGoodsAndServicesSold"]
)
# ROE
quarterly_fundamentals["ROE"] = (
    quarterly_fundamentals["netIncome"]
    / quarterly_fundamentals["totalShareholderEquity"]
)
# ROA
quarterly_fundamentals["ROA"] = (
    quarterly_fundamentals["netIncome"] / quarterly_fundamentals["totalAssets"]
)

# Calculo del book value para evaluacion del precio
quarterly_fundamentals["bookValue"] = (
    quarterly_fundamentals["totalAssets"] - quarterly_fundamentals["totalLiabilities"]
) / quarterly_fundamentals["commonStock"]


# Guardamos los datos
quarterly_fundamentals.to_csv("data/fundamentals.csv", index=True)
