import React, { useState, useEffect } from "react";
import "./RatingDetails.css";
import attributeDescriptions from "./AttributeDescriptions.json";

const RatingDetails = ({ ratingDetails }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [hoveredItem, setHoveredItem] = useState(null);
  const [, setDescriptions] = useState({});

  const toggleModal = () => {
    setIsOpen(!isOpen);
  };

  const handleMouseEnter = (key) => {
    setHoveredItem(key);
  };

  const handleMouseLeave = () => {
    setHoveredItem(null);
  };

  useEffect(() => {
    setDescriptions(attributeDescriptions);
  }, []);

  const ratings = Object.entries(ratingDetails).map(([key, value]) => {
    if (typeof value === "object" && value !== null) {
      return Object.entries(value).map(([innerKey, innerValue]) => (
        <div
          key={innerKey}
          className="rating-bar-container"
          onMouseEnter={() => handleMouseEnter(innerKey)}
          onMouseLeave={handleMouseLeave}
        >
          <label>
            {innerKey}: {innerValue}
          </label>
          <div
            className="rating-bar"
            style={{
              width: `${Math.min(100, Math.abs(innerValue))}%`,
              backgroundColor: innerValue >= 0 ? "green" : "red",
            }}
          ></div>
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
      <button onClick={toggleModal} className="rating-details-button">
        Details
      </button>
      {isOpen && (
        <>
          <div className="backdrop" onClick={toggleModal}></div>
          <div className="rating-details-modal">
            <button onClick={toggleModal} className="close-modal">
              X
            </button>
            <h2 className="rating-modal-title"> Calification Summary </h2>
            {ratings}
          </div>
        </>
      )}
    </>
  );
};

export default RatingDetails;
