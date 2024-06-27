import React, { useState } from "react";

// Funcion para renderizar el buscador
function BuscadorTicker({ onSearch }) {
  const [ticker, setTicker] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [inputError, setInputError] = useState(false);

  // Funcion para comprobar el input en el form
  const handleSubmit = (e) => {
    e.preventDefault();
    if (/^[A-Za-z0-9.]+$/.test(ticker)) {
      setIsLoading(true);
      onSearch(ticker.toUpperCase());
      setInputError(false);
    } else {
      setInputError(true);
    }
  };

  return (
    <>
      <div className={isLoading ? "loading ticker-display-wrapper" : "hidden"}>
        <p className="ticker-display-title">{ticker.toUpperCase()}</p>
        <p>Downloading data and making predictions</p>
      </div>
      <form
        onSubmit={handleSubmit}
        className={!isLoading ? "form_box" : "hidden"}
      >
        <label className="search_box">
          Enter a ticker:
          <input
            className="ticker_input"
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
          />
        </label>
        {inputError && (
          <p style={{ marginTop: 0, marginBottom: "1rem" }}>
            Invalid ticker format
          </p>
        )}
        <button className={"search_button"} type="submit">
          SEARCH
        </button>
      </form>
    </>
  );
}

export default BuscadorTicker;
