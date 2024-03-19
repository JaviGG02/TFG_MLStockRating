# Flask
from flask import Flask, jsonify, request
from flask_cors import CORS
# Gestion de los datos
import pandas as pd
import numpy as np
import json
from datetime import timedelta
import time
# Gestion de funciones auxiliares
from data_loader import download_financial_data, preprocess_financial_data, closest_price_from_df, replace_values_in_nested_dict
from predictions import make_predictions

# Flask App
app = Flask(__name__)
CORS(app)

@app.route('/api/datos', methods=['POST'])
def obtener_datos():
    """
    Función para la gestión de las llamadas a backend desde el frontend.
    """

    contenido = request.json
    ticker = contenido['ticker']

    # Obtener los datos financieros
    fundamentals = download_financial_data(ticker)
    if type(fundamentals) == KeyError:
        respuesta = {
            'Error':  fundamentals.args[0]
        }
        return jsonify(respuesta), 200

    # Hacer la predicción y calificación
    data, prices_df = preprocess_financial_data(financials=fundamentals, need_prices=True)
    # Hacemos predicciones
    predictions, calification = make_predictions(data)

    # Trasnsformar la lista de predicciones y los precios de data a diccionario
    predictions_df = pd.DataFrame(predictions, columns=['predicted_1y_sharePrice'])
    predictions_df['fiscalDateEnding'] = data['fiscalDateEnding'] + timedelta(days=365)
    predictions_df['fiscalDateEnding'] = predictions_df['fiscalDateEnding'].dt.strftime('%Y-%m')
    predictions_dict = dict(zip(predictions_df['fiscalDateEnding'], predictions_df['predicted_1y_sharePrice']))

    data['fiscalDateEnding'] = data['fiscalDateEnding'].dt.strftime('%Y-%m')
    del fundamentals['TIME_SERIES_MONTHLY_ADJUSTED']
    fundamentals['TIME_SERIES_MONTHLY_ADJUSTED'] = dict(zip(data['fiscalDateEnding'], data['sharePrice']))
    print(fundamentals['TIME_SERIES_MONTHLY_ADJUSTED'])

    for fecha in predictions_df['fiscalDateEnding']:
        if fecha not in data['fiscalDateEnding'].values:
            fecha_objetivo = pd.to_datetime(fecha, format='%Y-%m')
            closest_price = closest_price_from_df(fecha_objetivo, prices_df)
            fundamentals['TIME_SERIES_MONTHLY_ADJUSTED'][fecha] = closest_price.values[0]

    fundamentals = replace_values_in_nested_dict(d=fundamentals, old_values=['nan', 'NaN', 'N/A'], new_value="None")

    # Preparar la respuesta
    respuesta = {
        'datos_financieros': fundamentals,
        'prediccion': predictions_dict,
        'calificacion': calification
    }

    return jsonify(respuesta), 200

if __name__ == '__main__':
    app.run(debug=True)