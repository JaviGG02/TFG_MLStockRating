import finnhub
import json
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from yahoo_fin import stock_info as si

# Obtenemos las claves para las apis
with open(f"config.json", 'r') as file:
    config = json.load(file)

alphavantage_key = config["Alphavantage_key"]
finnhub_key = config["Finnhub_key"]


def closest_price_from_df(date_str: str, df_prices: pd.DataFrame(), symbol: str):
    """
    Funcion para obtener la fila del dataframe de precios con la fecha mas cercana al dia indicado
    """
    # Pasando la fecha e indice a datetime
    df_prices.index = pd.to_datetime(df_prices.index)
    fecha_objetivo = pd.to_datetime(date_str)
    # Calcular la diferencia absoluta entre la fecha objetivo y todas las fechas en el indice
    diferencias = abs(df_prices.index - fecha_objetivo)
    # Encuentra la fecha con la diferencia minima, menor a 40 dias
    fecha_mas_cercana = df_prices.index[diferencias.argmin()]
    if abs(fecha_objetivo-fecha_mas_cercana) > pd.Timedelta(days=40):
        return None 
    return df_prices.loc[fecha_mas_cercana, symbol]

def calcular_fundamentales(operacion: str, claves: tuple, datos: dict):
    """
    Funcion para realizar los calculos del mapeo
    """
    result = 0
    for clave in claves:
        valor = datos.get(clave)
        if valor is not None:
            if operacion == 'suma':
                result += valor
            elif operacion == 'resta':
                result -= valor
        else:
            return None
    return result

def get_prices(ticker: str):
    """
    Funcion para la obtencion del historial de precios de un ticker
    """
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&outputsize=full&symbol={ticker}&apikey={alphavantage_key}'
    r = requests.get(url)
    prices = r.json()
    # Caso de superar el limite de acccesos por minuto de la API 
    while 'Note' in prices:
        print("Waiting for 20 seconds for AlphaVantage API limit!")
        time.sleep(20)
        r = requests.get(url)
        prices = r.json()
    return prices
    
def process_topic(topic, map_dict, datos_mapeados):
    """
    Funcion para el mapeo de los elementos en funcion del topic
    """
    clave_map_dict = map_dict.get(topic['concept'])
    if clave_map_dict:
        try:
            datos_mapeados[clave_map_dict] = int(topic['value'])
        except ValueError:
            pass
    return datos_mapeados

def map_fundamentals(ticker, df_prices, remove_prefix="us-gaap_"): 
    """
    Funcion para mapear los datos de FinnHub a AlphaVantage y appendear los precios
    """
    mapeo_ic = {
        "IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity": "netIncomeFromContinuingOperations",
        "ResearchAndDevelopmentExpense": "researchAndDevelopment",
        "NetIncomeLoss": "netIncome",
        "OperatingIncomeLoss": "operatingIncome",
        "CostOfGoodsAndServicesSold": "costofGoodsAndServicesSold",
        "SellingGeneralAndAdministrativeExpense": "sellingGeneralAndAdministrative",
        "IncomeLossFromContinuingOperations": "incomeBeforeTax",
        "OtherNonoperatingIncomeExpense": "otherNonOperatingIncome",
        "IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest": "netIncomeFromContinuingOperations",
        "IncomeTaxExpenseBenefit": "incomeTaxExpense",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": "incomeBeforeTax",
        "OtherComprehensiveIncomeLossNetOfTax": "comprehensiveIncomeNetOfTax",
        "ComprehensiveIncomeNetOfTax": "comprehensiveIncomeNetOfTax",
        "InterestExpense": "interestAndDebtExpense",
        "ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest": "comprehensiveIncomeNetOfTax",
        "InterestExpense": "interestExpense",
        "DepreciationDepletionAndAmortization": "depreciationAndAmortization",
        "OtherDepreciationAndAmortization": "depreciationAndAmortization",
        "Revenues": "totalRevenue",
        "GainLossOnDispositionOfAssets": "nonInterestIncome",
        "GrossProfit": "grossProfit",
        "OperatingExpenses": "operatingExpenses",
    }

    mapeo_bs = {
        "RetainedEarningsAccumulatedDeficit": "retainedEarnings",
        "LongTermDebtNoncurrent": "longTermDebtNoncurrent",
        "StockholdersEquity": "totalShareholderEquity",
        "OtherAssetsNoncurrent": "otherNonCurrentAssets",
        "AssetsCurrent": "totalCurrentAssets",
        "AccountsReceivableNetCurrent": "currentNetReceivables",
        "PrepaidExpenseAndOtherAssetsCurrent": "otherCurrentAssets",
        "AccountsPayableCurrent": "currentAccountsPayable",
        "OtherLiabilitiesCurrent": "otherCurrentLiabilities",
        "OtherLiabilitiesNoncurrent": "otherNonCurrentLiabilities",
        "InventoryNet": "inventory",
        "LiabilitiesCurrent": "totalCurrentLiabilities",
        "CommonStockValue": "commonStock",
        "ShortTermInvestments": "shortTermInvestments",
        "ShortTermBorrowings": "shortTermDebt",
        "EquityMethodInvestments": "investments",
        "Assets": "totalAssets",
        "Goodwill": "goodwill",
        "CashAndCashEquivalentsAtCarryingValue": "cashAndCashEquivalentsAtCarryingValue",
        "TreasuryStockValue": "treasuryStock",
        "PropertyPlantAndEquipmentNet": "propertyPlantEquipment",
        "PrepaidExpenseAndOtherAssetsCurrent": "currentDebt",
        "OperatingLeaseLiabilityNoncurrent": "capitalLeaseObligations",
        "WeightedAverageNumberOfSharesOutstandingBasic": "commonStockSharesOutstanding"
    }

    mapeo_cf = {
        "NetCashProvidedByUsedInOperatingActivities": "operatingCashflow",
        "IncreaseDecreaseInAccountsPayableAndAccruedLiabilities": "changeInOperatingLiabilities",
        "DepreciationDepletionAndAmortization": "depreciationDepletionAndAmortization",
        "PaymentsToAcquirePropertyPlantAndEquipment": "capitalExpenditures",
        "IncreaseDecreaseInAccountsReceivable": "changeInReceivables",
        "IncreaseDecreaseInInventories": "changeInInventory",
        "NetCashProvidedByUsedInInvestingActivities": "cashflowFromInvestment",
        "NetCashProvidedByUsedInFinancingActivities": "cashflowFromFinancing",
        "ProceedsFromRepaymentsOfShortTermDebt": "proceedsFromRepaymentsOfShortTermDebt",
        "PaymentsForRepurchaseOfCommonStock": "paymentsForRepurchaseOfCommonStock",
        "PaymentsOfDividends": "dividendPayout",
        "ProceedsFromIssuanceOfSharesUnderIncentiveAndShareBasedCompensationPlansIncludingStockOptions": "proceedsFromIssuanceOfCommonStock",
        "ProceedsFromIssuanceOfLongTermDebt": "proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet",
        "ProceedsFromIssuanceOfCommonStock": "proceedsFromIssuanceOfCommonStock",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect": "changeInCashAndCashEquivalents",
        "NetIncomeLoss": "netIncome"
    }
    datos_calculos = {
        # Income
        "Revenues": None,
        "CostOfGoodsAndServicesSold": None,
        "DepreciationDepletionAndAmortization": None,
        "OperatingIncomeLoss": None,
        # Balance
        "LongTermDebtNoncurrent": None,
        "ShortTermBorrowings": None,
        "Assets": None,
        "StockholdersEquity": None,
        "OperatingLeaseLiabilityNoncurrent": None,
        "NetCashProvidedByUsedInFinancingActivities": None,
        "MarketableSecuritiesCurrent": None,
        "EquityMethodInvestments": None,
        "ShareBasedCompensation": None,
        "AccountsReceivableNetCurrent": None,
        "AssetsCurrent": None,
        # Other
        "unit": None
    }
    # Obtencion de los datos fundamentales de FinnHub
    finnhub_client = finnhub.Client(api_key=finnhub_key)
    try:
        datos_finnhub = finnhub_client.financials_reported(symbol=ticker, freq='quarterly')['data']
    except finnhub.FinnhubAPIException:
        return None

    result = {}
    for quarterly_fundamentals in datos_finnhub:
        datos_mapeados = {}
        for fundamental in quarterly_fundamentals['report']:
            for topic in quarterly_fundamentals['report'][fundamental]:
                # Caso para eliminar el prefijo, en caso de haberlo
                try:
                    topic['concept'] = topic['concept'][len(remove_prefix):]
                except TypeError:
                    continue
                # Caso para guardar el dato y posteriormente procesar calculos
                if topic['concept'] in datos_calculos:
                    try:
                        datos_calculos[topic['concept']] = int(topic['value'])
                    except ValueError:
                        pass
                # Income
                datos_mapeados = process_topic(topic, mapeo_ic, datos_mapeados)
                # Balance
                datos_mapeados = process_topic(topic, mapeo_bs, datos_mapeados)
                # Cash Flow
                datos_mapeados = process_topic(topic, mapeo_cf, datos_mapeados)
                
                if datos_calculos['unit'] == None: # Guardamos la unidad de la moneda empleada
                    datos_calculos['unit'] = topic['unit']

        # Completando los datos a traves de operaciones
        operaciones = [
            # CALCULOS INCOME STATEMENT
            ('grossProfit', 'resta', ('Revenues', 'CostOfGoodsAndServicesSold')),
            ('operatingExpenses', 'resta', ('Revenues', 'CostOfGoodsAndServicesSold', 'OperatingIncomeLoss')),
            ('ebit', 'suma', ('netIncome', 'interestExpense', 'incomeTaxExpense')),
            ('ebitda', 'suma', ('ebit', 'depreciationAndAmortization')),
            # CALCULOS BALANCE SHEET
            ('shortLongTermDebtTotal', 'suma', ('LongTermDebtNoncurrent', 'ShortTermBorrowings')),
            ('totalLiabilities', 'resta', ('Assets', 'StockholdersEquity')),
            ('capitalLeaseObligations', 'suma', ('OperatingLeaseLiabilityNoncurrent', 'NetCashProvidedByUsedInFinancingActivities')),
            ('investments', 'suma', ('MarketableSecuritiesCurrent', 'EquityMethodInvestments')),
            ('currentNetReceivables', 'suma', ('ShareBasedCompensation', 'AccountsReceivableNetCurrent')),
            ('totalNonCurrentAssets', 'resta', ('Assets', 'AssetsCurrent'))
        ]
        for destino, operacion, claves, in operaciones:
            if destino not in datos_mapeados:
                datos_mapeados[destino] = calcular_fundamentales(operacion, claves, datos_calculos)

        # Adding variables faltantes
        date = quarterly_fundamentals["endDate"][:-9]
        datos_mapeados["reportedCurrency"] = datos_calculos['unit']
        datos_mapeados["symbol"] = ticker
        datos_mapeados["sharePrice"] = closest_price_from_df(date, df_prices, ticker)
        # Variable objetivo
        date_1y = date = datetime.strptime(date, '%Y-%m-%d')
        date_1y += timedelta(days=365)  # +1 year
        date_1y = date_1y.strftime('%Y-%m-%d')
        datos_mapeados["1y_sharePrice"] = closest_price_from_df(date_1y, df_prices, ticker)

        result[date] = datos_mapeados    

    return result
    
tickers = si.tickers_nasdaq()

# DataFrames para almacenar los datos fundamentales y los precios
fundamentals_df = pd.DataFrame()
prices_df = pd.DataFrame()

# Bucle para procesar cada ticker
for i, ticker in enumerate(tickers):
    print(f"Obteniendo los datos de {ticker} \ number:{i}")

    # Obtencion de los precios del ticker
    prices = get_prices(ticker)

    # Almacenamiento del cierre del precio ajustado en base a fechas
    try:
        adjusted_close = {date: values['5. adjusted close'] for date, values in prices['Monthly Adjusted Time Series'].items()}
    except KeyError:
        continue
    diccionario_precios = {}
    diccionario_precios[ticker] = adjusted_close
    prices_symbol = pd.DataFrame.from_dict(diccionario_precios, orient='columns')
    prices_df = prices_df.merge(prices_symbol, left_index=True, right_index=True, how='outer')
    
    # Obtenemos los datos de FinnHub y mapeamos los datos
    datos_finnhub= map_fundamentals(ticker, prices_symbol)
    if datos_finnhub:
        finnhub_df = pd.DataFrame.from_dict(datos_finnhub, orient='index')
        # Aquellas filas sin informacion son eliminadas
        finnhub_df = finnhub_df.dropna(axis=1, how='all')
        fundamentals_df = pd.concat([fundamentals_df, finnhub_df])

    # Guardamos los dataframes cada 500 tickers
    if i%500 == 0:
        # Fundamentales
        fundamentals_df.index.names = ['fiscalDateEnding']
        fundamentals_df.reset_index(level='fiscalDateEnding')
        fundamentals_df.to_csv('2finnhub_mapped_quarterly.csv', index=True)
        # Precios
        prices_df.index.names = ['fiscalDateEnding']
        prices_df.reset_index(level='fiscalDateEnding')
        prices_df.to_csv('2alphavantage_prices_monthly.csv', index=True)

print("Descarga de datos completada")
