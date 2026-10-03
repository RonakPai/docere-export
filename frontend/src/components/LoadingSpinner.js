import React from "react";
import "../css/LoadingSpinner.css"; // Import the CSS for the spinner

const LoadingSpinner = () => {
  return (
    <div className="spinning-loading-container">
      <div className="spinner"></div>
    </div>
  );
};

export default LoadingSpinner;
