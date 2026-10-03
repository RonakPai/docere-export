import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../css/ErrorOverlay.css"; // Import the CSS for the spinner

const ErrorOverlay = ({ error }) => {
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if ("message" in error) {
      setErrorMessage(error.message);
    } else {
      setErrorMessage(error.toString());
    }
  }, [error]);
  return (
    <div className="error-overlay">
      <div className="error-container">
        <div className="error-title">Something Went Wrong</div>
        <div className="error-message">{errorMessage}</div>
        <button
          type="button"
          className="overlay-home-btn"
          onClick={() => {
            navigate("/home");
            window.location.reload();
          }}
        >
          Go Home
        </button>
      </div>
    </div>
  );
};

export default ErrorOverlay;
