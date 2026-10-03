import { React, useState, useEffect } from "react";
import LessonStart from "../components/LessonStart";
import LessonChat from "../components/LessonChat";
import LessonAnalysis from "../components/LessonAnalysis";
import { useLocation, useNavigate } from "react-router-dom";
import "../css/LessonPage.css";
import Navbar from "../components/Navbar";
import axios from "axios";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorOverlay from "../components/ErrorOverlay";
import { getCookie, baseURL } from "../functions/Funcs";
axios.defaults.timeout = 1000000;

function LessonPage() {
  const [lessonStatus, setLessonStatus] = useState("not-started");
  const [assignmentData, setAssignmentData] = useState({
    assignment_title: "",
    topic: "",
    creator_username: "",
  });
  const [report, setReport] = useState({});
  const location = useLocation();
  const navigate = useNavigate();
  const data = location.state || {};
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const userEmail = getCookie("userEmail");

  const handleStartClick = () => {
    setLessonStatus("chat");
  };

  const onViewAnalysis = async (username, attempt) => {
    setLoading(true);
    const response = await axios.post(
      `${baseURL}/generate_assignment_report/`,
      {
        assignment_id: data.assignmentId,
        student_username: username,
        student_attempt: attempt,
      }
    );
    let curReport = response.data;
    if (assignmentData.hide_assignment_answer === 0) {
      const progress = await axios.post(`${baseURL}/get_assignment_progress/`, {
        assignment_id: data.assignmentId,
        student_username: username,
        student_attempt: attempt,
      });
      curReport["Lesson Summary"] = progress.data.ai_augmented_lesson;
    }
    setReport(curReport);
    setLoading(false);
  };

  const regenerateAssignment = async () => {
    setLoading(true);
    const response = await axios.post(`${baseURL}/regenerate_assignment/`, {
      assignment_id: data.assignmentId,
      student_username: userEmail,
      student_attempt: data.attemptNumber,
    });
    if ("status" in response.data && response.data.status === "Error.") {
      setError(response.data);
    } else {
      setLoading(false);
      navigate("/lesson", {
        state: {
          assignmentId: response.data.assignment_id,
          studentUsername: response.data.student_username,
          attemptNumber: response.data.student_attempt,
        },
      });
      window.location.reload();
    }
  };

  useEffect(() => {
    if (!getCookie("userEmail")) {
      navigate("/");
    }
    if ("assignmentId" in data === false) {
      navigate("/home");
    }
    async function fetchData() {
      setLoading(true);
      try {
        const response = await axios.post(`${baseURL}/get_assignment_info/`, {
          assignment_id: data.assignmentId,
        });
        setAssignmentData(response.data);
        setLoading(false);
      } catch (e) {
        console.log("Error getting assignment info:", e);
      }
    }
    fetchData();
  }, []);

  return (
    <div>
      <Navbar />
      <div className="lesson-page">
        <div class="lesson-go-back" onClick={() => navigate("/home")}>
          <span class="go-back-arrow">←</span>
          Go Back
        </div>
        <div className="question-column">
          <h1>{assignmentData.assignment_title}</h1>
          <br />
          <div className="created-by">
            Creator: {assignmentData.creator_name}
          </div>
          <div className="attempt-number">
            Attempt Number: {data.attemptNumber}
          </div>
          <div className="description">{assignmentData.topic}</div>
          {lessonStatus === "not-started" && (
            <button
              type="button"
              className="start-button"
              onClick={handleStartClick}
            >
              Go To Chat
            </button>
          )}
          {report &&
            Object.keys(report).length > 0 &&
            data.studentUsername === userEmail && (
              <button
                type="button"
                className="start-button"
                onClick={regenerateAssignment}
              >
                Regenerate Assignment
              </button>
            )}
        </div>
        {report && Object.keys(report).length > 0 ? ( // If the report is not empty, show LessonAnalysis
          <LessonAnalysis report={report} />
        ) : lessonStatus === "not-started" ? ( // Otherwise, show either LessonStart or LessonChat
          <LessonStart />
        ) : (
          <LessonChat
            studentUsername={data.studentUsername}
            attemptNumber={data.attemptNumber}
            assignment={assignmentData}
            viewAnalysis={onViewAnalysis} // Passing the callback to view analysis
          />
        )}
      </div>
      {loading && <LoadingSpinner />}
      {error && <ErrorOverlay error={error} />}
    </div>
  );
}

export default LessonPage;
