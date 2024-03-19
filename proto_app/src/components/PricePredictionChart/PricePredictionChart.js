import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale } from 'chart.js';
import 'chartjs-adapter-date-fns';
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale);



// Funcion para el renderizado del grafico de precios y predicciones
const PricePredictionChart = ({ datosFinancieros, predicciones }) => {

  if (!datosFinancieros || !predicciones) {
    return <p>Cargando datos...</p>;
  }

  const fechasReales = datosFinancieros ? Object.keys(datosFinancieros.TIME_SERIES_MONTHLY_ADJUSTED) : [];
  const fechasPredicciones = predicciones ? Object.keys(predicciones) : [];
  const fechasUnificadas = [...new Set([...fechasReales, ...fechasPredicciones])].sort();
  const preciosRealesRellenados = fechasUnificadas.map(fecha => fechasReales.includes(fecha) ? datosFinancieros.TIME_SERIES_MONTHLY_ADJUSTED[fecha] : null);
  const preciosPrediccionesRellenados = fechasUnificadas.map(fecha => fechasPredicciones.includes(fecha) ? predicciones[fecha] : null);

  const data = {
  labels: fechasUnificadas,
  datasets: [
      {
      label: 'Precio Real',
      data: preciosRealesRellenados,
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
      },
      {
      label: 'Predicción',
      data: preciosPrediccionesRellenados,
      borderColor: 'rgb(255, 99, 132)',
      backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
  ],
  };

  const options = {
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'month',
          min: fechasUnificadas[0],
          max: fechasUnificadas[fechasUnificadas.length - 1],
          tooltipFormat: 'MMM yyyy',
        }
      },
      y: {
        title: {
          display: true,
          text: 'Precio:' + datosFinancieros.OVERVIEW.Currency,
        },
      },
    },
    elements: {
      line: {
        tension: 0.4,
        spanGaps: true,
      },
      point: {
        radius: 2,
      },
    },
  };

  return <Line data={data} options={options} />;
}

export default PricePredictionChart;
