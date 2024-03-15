import React, { useState } from 'react';

function BuscadorTicker({ onSearch }) {
  const [ticker, setTicker] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(ticker);
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Introduce un ticker:
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
        />
      </label>
      <button type="submit">BUSCAR</button>
    </form>
  );
}

export default BuscadorTicker;
