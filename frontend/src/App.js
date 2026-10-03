import React from "react";
import HomePage from "./pages/HomePage.js";
import CreateLessonPage from "./pages/CreateLessonPage.js";
import FinalizeLessonPage from "./pages/FinalizeLessonPage.js";
import DemoPage from "./pages/DemoPage.js";
import LessonPage from "./pages/LessonPage.js";
import LoginPage from "./pages/LoginPage.js";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import "./css/Global.css";
import OnboardingPage from "./pages/OnboardingPage.js";
import ResultsPage from "./pages/ResultsPage.js";
import ProfilePage from "./pages/ProfilePage.js";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/create-lesson" element={<CreateLessonPage />} />
        <Route path="/finalize-lesson" element={<FinalizeLessonPage />} />
        <Route path="/lesson" element={<LessonPage />} />
        <Route path="/demo" element={<DemoPage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </Router>
  );
}

export default App;
