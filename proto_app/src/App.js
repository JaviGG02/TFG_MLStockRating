// Importando librerías y paquetes
import React, { useState, useEffect } from 'react';

// Importando componentes
import BuscadorTicker from './components/BuscadorTicker/BuscadorTicker';
import OverviewComponent from './components/OverviewComponent/OverviewComponent';
import PricePredictionChart from './components/PricePredictionChart/PricePredictionChart';
import FinancialTable from './components/FinancialTable/FinancialTable';

// Importando estilos
import './components/BuscadorTicker/BuscadorTicker.css'
import './components/FinancialTable/FinancialTable.css'
import './components/OverviewComponent/OverviewComponent.css';
import './App.css';

function App() {
  
  const [data, setData] = useState({
    cargando: true,
    datosFinancieros: null,
    predicciones: null,
    calificacion: null,
    mensajeError: ''
  });

  useEffect(() => {
    console.log(data)
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
      if (!responseData.Error) { 
        setData({ // No error
          cargando: false,
          datosFinancieros: responseData.datos_financieros, 
          predicciones: responseData.prediccion, 
          calificacion: responseData.calificacion,
        }); 
      }
      else { // Error en backend
        setData({
          cargando: false, 
          mensajeError: responseData.Error
        });
      }
      
    })
    .catch(error => { // Error en frontend o backend
      console.error('Error:', error);
      setData({ ...data, cargando: false, mensajeError: 'An error occured while loading the data'}); 
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
            <p className='error-message'>Error: {data.mensajeError}</p>
          )}
        </>
      )}
    </div>
  );
}

export default App;
