import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
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

  const data = fechasUnificadas.map((fecha) => ({
    fecha,
    PrecioReal: fechasReales.includes(fecha)
      ? datosFinancieros.TIME_SERIES_MONTHLY_ADJUSTED[fecha]
      : null,
    Predicción: fechasPredicciones.includes(fecha) ? predicciones[fecha] : null,
  }));

  return (
    <ResponsiveContainer width={900} height={400}>
      <LineChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="fecha" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey="PrecioReal"
          stroke="#8884d8"
          dot={{ fill: "#8884d8" }}
        />
        <Line
          type="monotone"
          dataKey="Predicción"
          stroke="#ff6347"
          dot={{ fill: "#ff6347" }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default PricePredictionChart;
