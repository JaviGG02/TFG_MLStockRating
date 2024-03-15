# Flask
from flask import Flask, jsonify, request
from flask_cors import CORS
# Gestion de los datos
import pandas as pd
import time
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

    # Preparar la respuesta
    respuesta = {
        'datos_financieros': fundamentals,
        'prediccion': predictions,
        'calificacion': calification
    }
    
    return jsonify(respuesta), 200

if __name__ == '__main__':
    app.run(debug=True)