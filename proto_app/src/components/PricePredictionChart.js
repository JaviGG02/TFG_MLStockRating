import React, { useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale } from 'chart.js';
import 'chartjs-adapter-date-fns';
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale);




const PricePredictionChart = ({ datosFinancieros, predicciones }) => {

  if (!datosFinancieros || !predicciones) {
    return <p>Cargando datos...</p>; // O cualquier otro marcador de posición o lógica que prefieras
  }

  // Extraer las fechas y precios reales
  const fechasReales = datosFinancieros ? Object.keys(datosFinancieros.TIME_SERIES_MONTHLY_ADJUSTED) : [];
  const preciosReales = datosFinancieros ? Object.values(datosFinancieros.TIME_SERIES_MONTHLY_ADJUSTED) : [];

  // Extraer las fechas y precios de las predicciones
  const fechasPredicciones = predicciones ? Object.keys(predicciones) : [];
  const preciosPredicciones = predicciones ? Object.values(predicciones) : [];

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
        },
      },
    },
    elements: {
      line: {
        tension: 0.4, // Habilita líneas curvas
        spanGaps: true, // Esto hará que las líneas se unan, ignorando los 'null'
      },
      point: {
        radius: 2, // Tamaño de los puntos
      },
    },
  };

  return <Line data={data} options={options} />;
};

export default PricePredictionChart;
