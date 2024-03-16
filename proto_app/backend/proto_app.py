# Flask
from flask import Flask, jsonify, request
from flask_cors import CORS
# Gestion de los datos
import pandas as pd
import time
from datetime import timedelta
# Gestion de funciones auxiliares
from data_loader import download_financial_data, preprocess_financial_data
from predictions import make_predictions

# Flask App
app = Flask(__name__)
CORS(app)

@app.route('/api/datos', methods=['POST'])
def obtener_datos():
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
    data = preprocess_financial_data(fundamentals)
    # Hacemos predicciones
    predictions, calification = make_predictions(data)

    # Trasnsformar la lista de predicciones y los precios de data a diccionario
    predictions_df = pd.DataFrame(predictions, columns=['predicted_1y_sharePrice'])
    predictions_df['fiscalDateEnding'] = data['fiscalDateEnding'] + timedelta(days=365)
    predictions_df['fiscalDateEnding'] = predictions_df['fiscalDateEnding'].dt.strftime('%Y-%m-%d')
    predictions_dict = dict(zip(predictions_df['fiscalDateEnding'], predictions_df['predicted_1y_sharePrice']))
    
    data['fiscalDateEnding'] = data['fiscalDateEnding'].dt.strftime('%Y-%m-%d')
    fundamentals['TIME_SERIES_MONTHLY_ADJUSTED'] = dict(zip(data['fiscalDateEnding'], data['sharePrice']))

    # Preparar la respuesta
    respuesta = {
        'datos_financieros': fundamentals,
        'prediccion': predictions_dict,
        'calificacion': calification
    }
    
    return jsonify(respuesta), 200

if __name__ == '__main__':
    app.run(debug=True)