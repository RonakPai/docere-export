import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom"; // Import Link from react-router-dom
import "../css/navbar.css";

function Navbar({ onSearch }) {
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();

  const handleSearchChange = (event) => {
    const value = event.target.value;
    setSearchQuery(value);
    if (onSearch) {
      onSearch(value); // Pass the search query back to the parent if onSearch is provided
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <div className="navbar-logo">
          <Link to="/home">
            <img src="images/navbar-logo.png" alt="Docere Logo" />
          </Link>
        </div>
        <div className="navbar-option" onClick={() => navigate("/onboarding")}>
          <img src="images/question-mark.png" alt="Question Mark" />
          How to Use
        </div>
      </div>

      <div className="navbar-right">
        {onSearch && (
          <div className="navbar-search">
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Search for anything..."
            />
          </div>
        )}

        <div className="navbar-icons">
          <div className="navbar-option" onClick={() => navigate("/profile")}>
            <img src="images/profile.png" alt="Profile" />
            <div className="navbar-feedback">Profile</div>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
