
function OverviewComponent({ overview,  calificacion}) {

  console.log("LLEGANDO AQUI");
  console.log(calificacion);

  return (
    <div className="container">
      <div className="header">
        <h1 className="ticker">{overview.Symbol}</h1>
      </div>
      <div className="content">
        <div className="description">
          <div className="description_text">
            <h2>Description</h2>
            <p>{overview.Description}</p>
            <p className="sector">Sector: {overview.Sector}</p>
            <p className="sector">Calification: {calificacion}/5</p>
          </div>
          <div className="ratios">
            <div className="ratio">
              <strong>EPS (Earnings Per Share):</strong> 
              <span>{overview.EPS}</span>
            </div>
            <div className="ratio">
              <strong>Book Value:</strong> 
              <span>{overview.BookValue}</span>
            </div>
            <div className="ratio">
              <strong>Dividend Per Share:</strong> 
              <span>{overview.DividendPerShare !== "None" ? overview.DividendPerShare : "N/A"}</span>
            </div>
            <div className="ratio">
              <strong>ROA:</strong> 
              <span>{overview.ReturnOnAssetsTTM}</span>
            </div>
            <div className="ratio">
              <strong>ROE:</strong> 
              <span>{overview.ReturnOnEquityTTM}</span>
            </div>
            <div className="ratio">
              <strong>Reporting Currency:</strong> 
              <span>{overview.Currency}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default OverviewComponent;
