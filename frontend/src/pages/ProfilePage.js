import React, { useEffect, useState } from "react";
import "../css/ProfilePage.css";
import { getCookie, baseURL } from "../functions/Funcs.js";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
axios.defaults.timeout = 1000000;

const plans = [
  {
    name: "Free Plan",
    price: "Free",
    features: [
      "AI-Powered Performance Analysis",
      "Create & Join 3 Assignments/Month",
      "AI-Powered Regeneration Once Per Assignment",
    ],
    buttonText: "Active",
  },
  {
    name: "Student Plan",
    price: "$10 per month",
    features: [
      "AI-Powered Performance Analysis",
      "Create & Join 10 Assignments/Month",
      "AI-Powered Regeneration 5 Times Per Assignment",
      "Private Assignments (Max 1 Student)",
    ],
    buttonText: "Request Access",
    recommendedStudents: true,
  },
  {
    name: "Teacher Plan",
    price: "$100 per month",
    subtext: "Includes 30 Student Plans",
    features: [
      "AI-Powered Performance Analysis",
      "Create & Join 30 Assignments/Month",
      "AI-Powered Regeneration 5 Times Per Assignment",
      "Private Assignments (Unlimited Students)",
      "AI-Powered Lesson Simulations",
      "AI-Powered Classroom Performance Analysis (Coming Soon)",
      "AI-Powered Grading (Coming Soon)",
    ],
    buttonText: "Request Access",
    recommendedTeachers: true,
  },
  {
    name: "School Plan",
    price: "Contact for Pricing",
    subtext: "Includes Plans For All School Members",
    features: [
      "AI-Powered Performance Analysis",
      "Create & Join 1000 Assignments/Month",
      "AI-Powered Regeneration 5 Times Per Assignment",
      "Private Assignments (Unlimited Students)",
      "AI-Powered Lesson Simulations",
      "AI-Powered Classroom Performance Analysis (Coming Soon)",
      "AI-Powered Grading (Coming Soon)",
    ],
    buttonText: "Request Access",
    bestValue: true,
  },
];

function ProfilePage() {
  const navigate = useNavigate();
  const [activeIndex, setActiveIndex] = useState(0);
  const [joinedLessons, setJoinedLessons] = useState("Loading...");
  const [createdLessons, setCreatedLessons] = useState("Loading...");
  const userName = getCookie("userName");
  const userEmail = getCookie("userEmail");

  useEffect(() => {
    if (!getCookie("userName")) {
      navigate("/");
    }
    const fetchCreated = async () => {
      const response = await axios.post(
        `${baseURL}/get_all_created_assignments/`,
        { creator_username: userEmail }
      );
      setCreatedLessons(response.data.assignment_list.length);
    };
    const fetchJoined = async () => {
      const response = await axios.post(
        `${baseURL}/get_all_assigned_assignments/`,
        { student_username: userEmail }
      );
      setJoinedLessons(response.data.assignment_list.length);
    };
    fetchCreated();
    fetchJoined();
  });
  return (
    <div>
      <Navbar />
      <div className="profile-container">
        <div className="profile-sidebar">
          <ul>
            <li
              className={activeIndex === 0 ? "active-tab" : ""}
              onClick={() => setActiveIndex(0)}
            >
              <img src="images/profile.png" alt="account" />
              Account Information
            </li>
            <li
              className={activeIndex === 1 ? "active-tab" : ""}
              onClick={() => setActiveIndex(1)}
            >
              <img src="images/subscription.png" alt="billing" />
              Subscription Tier
            </li>
            <li
              onClick={() =>
                window.open(
                  "https://docs.google.com/forms/d/e/1FAIpQLScZgttYYn7ym3r9yTL8jmwmNiagyO02I8j6F9M5Ffo6YyhVfQ/viewform?usp=sf_link",
                  "_blank"
                )
              }
            >
              <img src="images/bug.png" alt="feedback" />
              Report a Bug
            </li>
            <li
              onClick={() =>
                window.open(
                  "https://docs.google.com/forms/d/e/1FAIpQLScOBRD0Pmxwjz3kAUplrJY2hVgIxKiRBK-6bNb059jeVhSU3A/viewform?usp=sf_link",
                  "_blank"
                )
              }
            >
              <img src="images/feedback.png" alt="feedback" />
              Send Feedback
            </li>
          </ul>
        </div>
        <div className="profile-content">
          {activeIndex === 0 ? (
            <div>
              <h2>Account Information</h2>
              <div className="profile-item-group">
                <label>Name</label>
                <input type="text" disabled value={userName} />
              </div>
              <div className="profile-item-group">
                <label>Email</label>
                <input type="text" disabled value={userEmail} />
              </div>
              <div className="profile-item-group">
                <label>Created Lessons</label>
                <input type="text" disabled value={createdLessons} />
              </div>
              <div className="profile-item-group">
                <label>Joined Lessons</label>
                <input type="text" disabled value={joinedLessons} />
              </div>
            </div>
          ) : (
            <div className="subscription-section">
              <h2>Subscription Tier</h2>
              <div className="plans-container">
                {plans.map((plan, index) => (
                  <div
                    key={index}
                    className={`plan-card ${
                      plan.recommendedStudents || plan.recommendedTeachers
                        ? "recommended"
                        : ""
                    } ${plan.bestValue ? "best-value" : ""}`}
                  >
                    {plan.recommendedStudents && (
                      <div className="badge">Recommended For Students</div>
                    )}
                    {plan.recommendedTeachers && (
                      <div className="badge">Recommended For Teachers</div>
                    )}
                    {plan.bestValue && <div className="badge">Best Value</div>}
                    <h3>{plan.name}</h3>
                    <p className="price">{plan.price}</p>
                    {plan.subtext && <p className="subtext">{plan.subtext}</p>}
                    <ul>
                      {plan.features.map((feature, idx) => (
                        <li key={idx}>{feature}</li>
                      ))}
                    </ul>
                    <button
                      className={"get-started " + plan.buttonText}
                      onClick={() => {
                        if (plan.buttonText === "Request Access") {
                          window.open(
                            "https://docerelearning.com/contact",
                            "blank"
                          );
                        }
                      }}
                    >
                      {plan.buttonText}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ProfilePage;
