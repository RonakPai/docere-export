import React, { useEffect, useState } from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import "../css/LoginPage.css";
import { GoogleOAuthKey } from "../keys.js";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { getCookie, baseURL } from "../functions/Funcs.js";
axios.defaults.timeout = 1000000;

function LoginPage() {
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (getCookie("userEmail")) {
      navigate("/home");
    }
  });

  const handleLoginSuccess = async (response) => {
    const tokenParts = response.credential.split(".");
    const payload = JSON.parse(atob(tokenParts[1]));

    const userName = payload.name;
    const userEmail = payload.email;

    const onboardResponse = await axios.post(`${baseURL}/onboard_user/`, {
      username: userEmail,
      name: userName,
      subscription_tier: "school",
    });

    if (onboardResponse.data.valid_user === false) {
      window.location.href = "https://docerelearning.com/contact";
    } else {
      document.cookie = `userName=${userName}; path=/; max-age=86400; SameSite=Strict`;
      document.cookie = `userEmail=${userEmail}; path=/; max-age=86400; SameSite=Strict`;
      await axios.post(`${baseURL}/update_name/`, {
        username: userEmail,
        name: userName,
      });
      if (onboardResponse.data.onboarded) {
        navigate("/onboarding");
      } else {
        navigate("/home");
      }
    }
  };

  const handleLoginFailure = (error) => {
    console.error("Google login failed", error);
  };

  return (
    <GoogleOAuthProvider clientId={GoogleOAuthKey}>
      <div className="login-container">
        <img
          src="images/home-page-logo.png"
          alt="Logo"
          className="center-image"
        />
        <div className="login-slogan">Learn By Teaching</div>
        <GoogleLogin
          onSuccess={handleLoginSuccess}
          onError={handleLoginFailure}
          useOneTap
          theme="filled_black"
        >
          <button id="google-login-button">Login with Google</button>
        </GoogleLogin>
      </div>
      <div
        className="login-learn-more"
        onClick={() => window.open("https://docerelearning.com", "_blank")}
      >
        About Us
      </div>
      {errorMessage !== "" && (
        <div className="loading-overlay">
          <div className="finished-loading-container">
            <div className="loading-message">Cannot Log-In</div>
            <div className="loading-subtext">
              We are running a closed beta, for more information contact
              ronak@docerelearning.com
            </div>
            <button
              type="button"
              className="overlay-home-btn"
              onClick={() =>
                (window.location.href = "https://docerelearning.com/contact")
              }
            >
              About Us
            </button>
          </div>
        </div>
      )}
    </GoogleOAuthProvider>
  );
}

export default LoginPage;
