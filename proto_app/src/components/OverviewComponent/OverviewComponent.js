import RatingDetails from "../RatingDetails/RatingDetails";

// Funcion para el renderizado del overview de la empresa
function OverviewComponent({ overview, calificacion }) {
  let component;
  if (calificacion !== "None") {
    component = (
      <div className="calification-div">
        <p className="sector">
          <strong>Calification:</strong> {calificacion.finalRate}/100
        </p>
        <RatingDetails ratingDetails={calificacion} />
      </div>
    );
  } else {
    component = (
      <p className="sector">
        <strong>Calification:</strong> Due to lack of data, a rating cannot be
        computed
      </p>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <h1 className="ticker">
          {overview.Name} ({overview.Symbol})
        </h1>
      </div>
      <div className="content">
        <div className="description">
          <div className="description_text">
            <h2>Description</h2>
            <p>{overview.Description}</p>
            <p className="sector">
              <strong>Sector:</strong> {overview.Sector}
            </p>
            {component}
          </div>
          <div className="ratios-div">
            <div className="ratio">
              <span>
                <strong>Quarterly Earnings Growth:</strong>{" "}
                {overview.QuarterlyEarningsGrowthYOY}
              </span>
            </div>
            <div className="ratio">
              <span>
                <strong>EPS (Earnings Per Share):</strong> {overview.EPS}
              </span>
            </div>
            <div className="ratio">
              <span>
                <strong>Dividend Date:</strong> {overview.DividendDate}
              </span>
            </div>
            <div className="ratio">
              <span>
                <strong>Dividend Per Share:</strong> {overview.DividendPerShare}
              </span>
            </div>
            <div className="ratio">
              <span>
                <strong>Book Value:</strong> {overview.BookValue}
              </span>
            </div>
            <div className="ratio">
              <span>
                <strong>ROA:</strong> {overview.ReturnOnAssetsTTM}
              </span>
            </div>
            <div className="ratio">
              <span>
                <strong>ROE:</strong> {overview.ReturnOnEquityTTM}
              </span>
            </div>
            <div className="ratio">
              <span>
                <strong>Reporting Currency:</strong> {overview.Currency}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default OverviewComponent;
