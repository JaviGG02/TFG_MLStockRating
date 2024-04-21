"""
Modulo encargado de habilitar y gestionar las llamadas al backend
"""

# Flask
from flask import Flask, jsonify, request
from flask_cors import CORS

# Gestion de funciones
from data_manager import DataManager

# Flask App
app = Flask(__name__)
CORS(app)


@app.route("/api/datos", methods=["POST"])
def obtener_datos():
    """
    Función para la gestión de las llamadas a backend desde el frontend.
    """

    contenido = request.json
    data_manager = DataManager(contenido["ticker"])

    # Obtener los datos financieros
    fundamentals = data_manager.download_financial_data()
    if "Error" in fundamentals:
        return jsonify(fundamentals), 200

    # Preparar los datos
    data_manager.preprocess_financial_data()
    # Hacer las predicciones
    data_manager.make_predictions()
    # Calcular nota
    data_manager.calculate_rating()
    # Preparar la respuesta
    data_manager.prepare_response()

    return jsonify(data_manager.respuesta), 200


if __name__ == "__main__":
    app.run(debug=True)
