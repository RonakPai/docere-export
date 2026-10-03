import React from "react";
import "../css/OnboardingPage.css";
import { useNavigate } from "react-router-dom";

const OnboardingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="onboarding-container">
      {/* Top half: Animated Logo */}
      <div className="logo-container">
        {/* Replace the src with your actual logo path */}
        <img
          src="images/home-page-logo.png"
          alt="Docere Logo"
          className="animated-logo"
        />
      </div>

      {/* Bottom section: How to Use + About + Button */}
      <div className="bottom-container">
        {/* Split left/right for sections */}
        <div className="sections">
          {/* How to Use Section */}
          <div className="how-to-use-section">
            <h2>How to Use</h2>
            <ul>
              <li>
                <b>Create:</b> Upload lesson materials to create personalized
                lessons
              </li>
              <li>
                <b>Learn:</b> Complete lessons by teaching concepts to Docere
              </li>
              <li>
                <b>Improve:</b> Receive feedback and regenerate lessons to
                target areas for growth
              </li>
            </ul>
            <iframe
              width="280"
              height="160"
              src="https://drive.google.com/file/d/1GTb7dnyZy-0YiTl3aXMVYD3W-BarBEdS/preview"
              title="Demo Video"
              frameBorder="0"
              allow="autoplay"
              allowFullScreen
            ></iframe>
            <div className="about-text">
              More demo videos are available at{" "}
              <a href="www.docerelearning.com"> www.docerelearning.com </a>
            </div>
          </div>

          {/* About Section */}
          <div className="about-section">
            <h2>About</h2>
            <p>
              We believe that Generative AI possesses the power to transform
              today’s education from a system focused on rote memorization to
              one focused on concept-based discourse, learning, and
              understanding. How? GenAI <b>extends teachers' reach</b> by
              spending the 1:1 time with the student that teachers cannot. This
              empowers teachers' curriculums (in-class practice, homework
              assignments, exams, etc.) to{" "}
              <b>shift away from current simpler assignments</b> that emphasize
              memorization towards paradigms that emphasize{" "}
              <b>real conceptual understanding</b> like discussing lengthy,
              multi-dimensional topics with GenAI-powered agents.
            </p>
            <p>
              To that end, the best way for students to understand complex
              concepts is done via students <b>teaching</b> the concepts to
              someone. Using Docere Learning, a student will apply what they
              know while teaching a GenAI-powered agent about a concept,
              ultimately
              <b>bolstering the student’s understanding</b> of this concept far
              better than any of today’s rote memorization-focused lessons
              could.
            </p>
          </div>
        </div>

        {/* "Ready to Learn?" button at the bottom */}
        <div className="ready-button-container">
          <button
            className="ready-button"
            onClick={() => {
              navigate("/home");
            }}
          >
            Ready to Learn?
          </button>
        </div>
      </div>
    </div>
  );
};

export default OnboardingPage;
