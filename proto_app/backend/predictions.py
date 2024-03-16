from data_loader import download_financial_data, preprocess_financial_data
from joblib      import dump, load
from datetime    import datetime, timedelta
from sklearn.base import clone
import pandas    as pd
import numpy     as np
import matplotlib.pyplot as plt
import matplotlib.dates  as mdates


def make_predictions(data: pd.DataFrame):
    """
    Función que toma los datos financieros procesados para hacer las predicciones y aportar una calificación en base al retorno esperado
    :data: dataframe de datos financieros procesados, se empleará para entrenar más el modelo y realizar las predicciones
    """
    print(f"Realizando predicciones")
    model = load(r'C:\Users\xavic\Escritorio\TFG_MLStockRating\proto_app\backend\gb_model.joblib')
    predictions = []
    for i in range(len(data)):    
        original_model = model # Modelo temporal para entrenamiento
        if not np.isnan(data.iloc[i]['1y_sharePrice']):
            # Entrenamiento
            y_train = data.iloc[:i+1]['1y_sharePrice']
            X_train = data.iloc[:i+1].drop(['1y_sharePrice'], axis=1)
            original_model.fit(X_train, y_train)
            # Prediccion
            X_next = data.iloc[[i+1]].drop(['1y_sharePrice'], axis=1)
            y_pred = model.predict(X_next) 
            predictions.append(float(y_pred.item()))
        else:
            # Prediccion final
            X_next = data.iloc[i:].drop(['1y_sharePrice'], axis=1)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_next) 
            for pred in list(y_pred):
                predictions.append(float(pred.item()))
            break

    pct_return = (predictions[-1] - data["sharePrice"].iloc[-1]) / predictions[-1]
    if pct_return < 0:
        calification = 1
    elif pct_return < 5:
        calification = 2
    elif pct_return < 10:
        calification = 3
    elif pct_return < 15:
        calification = 4;
    else:
        calification = 5

    return predictions, calification

def plot_data(ml_data: pd.DataFrame, predictions: list):
    """
    Función empleada para plottear el python los resultados comparados reales vs predichos
    :ml_data: dataframe con datos reales
    :predictions: lista de predicciones realizadas
    """
    ml_data['fiscalDateEnding'] = pd.to_datetime(ml_data['fiscalDateEnding'])
    predictions_df = pd.DataFrame(predictions, columns=['predicted_1y_sharePrice'])
    predictions_df['fiscalDateEnding'] = ml_data['fiscalDateEnding'].apply(lambda x: x + timedelta(days=365))

    plt.figure(figsize=(16, 6))

    # Añadir puntos para los valores reales
    plt.plot(ml_data['fiscalDateEnding'], ml_data['sharePrice'], 'o-', label='Real', alpha=0.7)
    # Añadir puntos para las predicciones
    plt.plot(predictions_df['fiscalDateEnding'], predictions_df['predicted_1y_sharePrice'], 'x-', label='Predicted', alpha=0.7)

    plt.xlabel('Fecha')
    plt.ylabel('1Y Share Price')
    plt.title('Real vs Predicted Share Prices')

    # Configurar el formato del eje X para mostrar una marca cada 3 meses
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    return 0

if __name__ == '__main__':
    for ticker in ['22UA']:
        # Obtenemos los datos
        diccionario = download_financial_data(ticker)
        if type(diccionario) == KeyError:
            print(diccionario.args[0])
            break
        data = preprocess_financial_data(diccionario)
        # Hacemos predicciones
        predictions_df, calification = make_predictions(data)
        print(calification)
        plot_data(data, predictions_df)
    