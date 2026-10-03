import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../css/ProfileHeader.css";
import axios from "axios";
import LoadingSpinner from "./LoadingSpinner";
import ErrorOverlay from "./ErrorOverlay";
import { baseURL, getCookie } from "../functions/Funcs";
axios.defaults.timeout = 1000000;

function ProfileHeader({ showOptions = false }) {
  const navigate = useNavigate();
  const [showLessonInput, setShowLessonInput] = useState(false);
  const [lessonId, setLessonId] = useState("");
  const [inputPosition, setInputPosition] = useState({ top: 0, left: 0 });
  const joinButtonRef = useRef(null);
  const userEmail = getCookie("userEmail");
  const userName = getCookie("userName");
  const [names, setNames] = useState(["UU"]);
  const [initials, setInitials] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const n = userName.trim().split(" ");
    const i =
      n.length === 1
        ? n[0][0].toUpperCase()
        : `${n[0][0].toUpperCase()}${n[n.length - 1][0].toUpperCase()}`;
    setNames(n);
    setInitials(i);
  }, []);

  const createLesson = () => {
    navigate("/create-lesson");
  };

  const joinLesson = async () => {
    closeInput();
    setLoading(true);
    const response = await axios.post(`${baseURL}/join_assignment/`, {
      assignment_id: lessonId,
      student_username: userEmail,
    });
    setLoading(false);
    if ("status" in response.data && response.data.status === "Error.") {
      setError(response.data);
      console.log(response.data.message);
    } else {
      navigate("/lesson", {
        state: {
          assignmentId: lessonId,
          studentUsername: userEmail,
          attemptNumber: 1,
        },
      });
    }
  };

  const handleJoinClick = () => {
    const rect = joinButtonRef.current.getBoundingClientRect();
    setInputPosition({
      top: rect.bottom + window.scrollY,
      left: rect.left + window.scrollX,
    });
    setShowLessonInput(true);
  };

  const closeInput = () => {
    setShowLessonInput(false);
    setLessonId("");
  };

  return (
    <div className="welcome-header">
      <div className="profile-pic">{initials}</div>
      <div>
        <h1>Welcome, {names[0]}</h1>
      </div>
      {showOptions && (
        <div className="button-container">
          <button
            ref={joinButtonRef}
            className="join-lesson"
            onClick={handleJoinClick}
          >
            Join Lesson
          </button>
          <button className="create-lesson" onClick={createLesson}>
            + Create Lesson
          </button>
        </div>
      )}

      {showOptions && showLessonInput && (
        <>
          <div className="lesson-id-overlay" onClick={closeInput}></div>
          <div
            className="lesson-input-container"
            style={{
              top: `${inputPosition.top}px`,
              left: `${inputPosition.left}px`,
            }}
          >
            <input
              type="text"
              placeholder="Enter Lesson ID"
              autoComplete="off"
              value={lessonId}
              onChange={(e) => setLessonId(e.target.value)}
              className="lesson-id-input"
            />
            <button onClick={joinLesson} className="create-lesson">
              Join
            </button>
          </div>
        </>
      )}
      {loading && <LoadingSpinner />}
      {error && <ErrorOverlay error={error} />}
    </div>
  );
}

export default ProfileHeader;
