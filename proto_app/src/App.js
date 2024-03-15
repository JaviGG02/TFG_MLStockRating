import React, { useState } from 'react';
import BuscadorTicker from './components/BuscadorTicker.js';
// import GraficoPrecios from './components/GraficoPrecios';
// Importar los demás componentes aquí

function App() {
  // const [datosFinancieros, setDatosFinancieros] = useState(null);

  const buscarTicker = (ticker) => {
    // Llamar a la API del backend para obtener los datos
    // Por ejemplo, usando fetch o axios
    fetch('http://localhost:5000/api/datos', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json', // Este encabezado indica que el cuerpo de la solicitud está en formato JSON
          },
          body: JSON.stringify({ ticker: ticker }), // Asegúrate de que el objeto que se convierte en JSON tiene la estructura esperada por el backend
        })
      .then(response => response.json())
      .then(data => {
        console.log('Datos recibidos del backend:', data);
        // setDatosFinancieros(data); // Guarda los datos en el estado si vas a usarlos
      })
      .catch(error => console.error('Error:', error));
  };

  return (
    <div>
      <BuscadorTicker onSearch={buscarTicker} />
    </div>
  );
}

export default App;