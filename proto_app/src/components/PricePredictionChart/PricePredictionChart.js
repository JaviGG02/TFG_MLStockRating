import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

const PricePredictionChart = ({ datosFinancieros, predicciones }) => {
  if (!datosFinancieros || !predicciones) {
    return <p>Cargando datos...</p>;
  }

  const fechasReales = Object.keys(
    datosFinancieros.TIME_SERIES_MONTHLY_ADJUSTED,
  );
  const fechasPredicciones = Object.keys(predicciones);
  const fechasUnificadas = [
    ...new Set([...fechasReales, ...fechasPredicciones]),
  ].sort();

  const data = fechasUnificadas.map((date) => ({
    date: date,
    RealPrice: fechasReales.includes(date)
      ? datosFinancieros.TIME_SERIES_MONTHLY_ADJUSTED[date]
      : null,
    Prediction: fechasPredicciones.includes(date) ? predicciones[date] : null,
  }));

  return (
    <LineChart
      data={data}
      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      width={900}
      height={400}
    >
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line
        type="monotone"
        dataKey="RealPrice"
        stroke="#8884d8"
        dot={{ fill: "#8884d8" }}
      />
      <Line
        type="monotone"
        dataKey="Prediction"
        stroke="#ff6347"
        dot={{ fill: "#ff6347" }}
      />
    </LineChart>
  );
};

export default PricePredictionChart;
