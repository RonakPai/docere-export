import React from "react";
import "../css/Tooltip.css";

function Tooltip({ text }) {
  return (
    <span className="tooltip-container">
      <img src="images/question-mark.png" alt="question" />
      <span className="tooltip-text">{text}</span>
    </span>
  );
}

export default Tooltip;
