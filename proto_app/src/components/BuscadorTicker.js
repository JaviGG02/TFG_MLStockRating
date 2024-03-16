import React, { useState } from 'react';

function BuscadorTicker({ onSearch }) {
  const [ticker, setTicker] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    onSearch(ticker);
  };

  return (
    <form onSubmit={handleSubmit} className={isLoading ? 'loading' : 'form_box'}>
      <label className='search_box'>
        Enter a ticker:
        <input
          className='ticker_input'
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
        />
      </label>
      <button className='search_button' type="submit">SEARCH</button>
    </form>
  );
}

export default BuscadorTicker;
