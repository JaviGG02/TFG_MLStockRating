import React, { useState } from 'react';
import './RatingDetails.css';

// Supongamos que tienes un objeto que mapea los keys a sus descripciones
const attributeDescriptions = {
  debtEquityRatio: "D/E: Ratio that is used to evaluate a company's financial leverage, it shows how the company gets financed \
                    rather by creditors (money that usually comes with interest) or shareholders. \
                    A value of 100 indicates that the company is equally or mostly financed by shareholders rather than by creditors (D/E <= 1). \
                    A negative value indicates that the company has negative equity, which indicates that it has more liabilities than \
                    assets, which should be seen as a high risk flag. (D/E < 0)",
  quickRatio: "QR: Measure of a company's ability to meet its short-term obligations with its most liquid assets.\
               A value of 100 indicates that the company is able to pay all its current liabilities with their current assets (QR >= 1).\
               A negative value indicates that the company would have problems repaying its debts (QR < 0).",
  dividendPayout: "Indicates how much the dividend payout has increased in overall quarter to quarter during the last 5 years. \
                   A calification of 60 in this rating indicates that quarter to quarter it has geometricly increased by 6%.",
  ebitda: "Indicates how much the earnings before interest, taxes, depreciation, and amortization has increased in overall \
           quarter to quarter during the last 5 years. This is an alternate measure of profitability to net income. A \
           calification of 60 in this rating indicates that quarter to quarter it has geometricly increased by 6%.",
  freeCashFlow: "Indicates how much free cash flow has increased in overall quarter to quarter during the last 5 years. \
                 This represents the cash that a company generates after accounting for cash outflows to support operations \
                 and maintain its capital assets. A calification of 60 in this rating indicates \
                 that quarter to quarter it has geometricly increased by 6%.",
  totalRevenue: "Indicates how much revenue has increased in overall quarter to quarter during the last 5 years. \
                 Revenue is money brought into a company by its business activities. A calification of 60 in this rating indicates \
                 that quarter to quarter it has geometricly increased by 6%.",
  ROA: "Ratio that indicates how much profitable or efficient is the company using its assets. \
        A value of 100 indicates that the company has surpassed a value usually considered safe (ROA > 5%). \
        A negative value indicates that the company is not generating any profits (ROA < 0%). ",
  ROE: "Ratio that indicates how much profitable or efficient is the company using its equity. \
        A value of 100 indicates that the company has surpassed a value usually considered safe (ROE > 20%). \
        A negative value indicates that the company is not generating any profits (ROE < 0%). ",
  bookValue: "With this attribute the calculated ratio is the Price to Book ratio (PB). It may be used to see if a company is overpriced or underpriced. \
              A value of 100 indicates that the share may be cheap, as the book value is higher than the current share price (PB < 1). \
              A negative value indicates that the equity is negative, which may be seen as a high risk factor (PB < 0).",
  netIncome: "Indicates how much net profits the company has been generating in overall quarter to quarter during the last 5 years. \
              A calification of 60 in this rating indicates that quarter to quarter it has geometricly increased by 6%."
};

const RatingDetails = ({ ratingDetails }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [hoveredItem, setHoveredItem] = useState(null);

  const toggleModal = () => {
    setIsOpen(!isOpen);
  };

  const handleMouseEnter = (key) => {
    setHoveredItem(key);
  };

  const handleMouseLeave = () => {
    setHoveredItem(null);
  };

  const ratings = Object.entries(ratingDetails).map(([key, value]) => {
    if (typeof value === 'object' && value !== null) {
      return Object.entries(value).map(([innerKey, innerValue]) => (
        <div key={innerKey} className="rating-bar-container" onMouseEnter={() => handleMouseEnter(innerKey)} onMouseLeave={handleMouseLeave}>
          <label>{innerKey}: {innerValue}</label>
          <div className="rating-bar" style={{ width: `${Math.min(100, Math.abs(innerValue))}%`, backgroundColor: innerValue >= 0 ? 'green' : 'red' }}></div>
          {hoveredItem === innerKey && (
            <div className="tooltip">{attributeDescriptions[innerKey]}</div>
          )}
        </div>
      ));
    }
    return null;
  });

  return (
    <>
      <button onClick={toggleModal} className="rating-details-button">Details</button>
      {isOpen && (
        <>
          <div className="backdrop" onClick={toggleModal}></div>
          <div className="rating-details-modal">
            <button onClick={toggleModal} className="close-modal">X</button>
            <h2 className='rating-modal-title'> Calification Summary </h2>
            {ratings}
          </div>
        </>
      )}
    </>
  );
};

export default RatingDetails;
