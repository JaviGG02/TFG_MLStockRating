import React, { useState, useEffect } from 'react';
import BuscadorTicker from './components/BuscadorTicker';
import OverviewComponent from './components/OverviewComponent';
import PricePredictionChart from './components/PricePredictionChart';
import FinancialTable from './components/FinancialTable';

import './styles.css';

function App() {
  // Usamos un solo objeto de estado para manejar todos los datos
  const [data, setData] = useState({
    cargando: true, // Nuevo estado para manejar la carga
    datosFinancieros: null,
    predicciones: null,
    calificacion: null,
  });

  useEffect(() => {
    console.log('Datos actualizados:', data);
  }, [data]);

  const buscarTicker = (ticker) => {
    fetch('http://localhost:5000/api/datos', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ticker: ticker }),
    })
    .then(response => response.json())
    .then(responseData => {
      setData({
        cargando: false, // Actualizamos el estado de carga
        datosFinancieros: responseData.datos_financieros, 
        predicciones: responseData.prediccion, 
        calificacion: responseData.calificacion,
      }); 
    })
    .catch(error => {
      console.error('Error:', error);
      setData({ ...data, cargando: false }); // Actualizamos solo el estado de carga
    });
  };

  return (
    <div className='root-div'>
      {data.cargando ? (
        <BuscadorTicker onSearch={buscarTicker} />
      ) : (
        <>
          {data.datosFinancieros && data.predicciones && data.calificacion !== null ? (
            <>
              <OverviewComponent overview={data.datosFinancieros.OVERVIEW} calificacion={data.calificacion} />
              <div className="page-container">
                <div className="graph-container">
                  <PricePredictionChart
                    datosFinancieros={data.datosFinancieros}
                    predicciones={data.predicciones}
                  />
                </div>
                <div className="table-container">
                  <FinancialTable 
                    incomeStatement={data.datosFinancieros.INCOME_STATEMENT.annualReports} 
                    balanceSheet={data.datosFinancieros.BALANCE_SHEET.annualReports} 
                    cashFlows={data.datosFinancieros.CASH_FLOW.annualReports}
                  />
                </div>
              </div>
            </>
          ) : (
            <p>Cargando datos...</p>
          )}
        </>
      )}
    </div>
  );
}

export default App;
