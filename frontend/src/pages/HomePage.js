import React, { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import ProfileHeader from "../components/ProfileHeader";
import { useNavigate } from "react-router-dom";
import "../css/HomePage.css";
import axios from "axios";
import LoadingSpinner from "../components/LoadingSpinner";
import { baseURL, getCookie } from "../functions/Funcs";
axios.defaults.timeout = 1000000;

function HomePage() {
  const [viewCreated, setViewCreated] = useState(true);
  const [lessonsInProgress, setLessonsInProgress] = useState([]);
  const [pastCreatedLessons, setPastCreatedLessons] = useState([]);
  const [pastJoinedLessons, setPastJoinedLessons] = useState([]);
  const [lessonsToJoin, setLessonsToJoin] = useState([]);
  const [filteredInProgressLessons, setFilteredInProgressLessons] = useState(
    []
  );
  const [filteredPastCreatedLessons, setFilteredPastCreatedLessons] = useState(
    []
  );
  const [filteredPastJoinedLessons, setFilteredPastJoinedLessons] = useState(
    []
  );
  const [filteredLessonsToJoin, setFilteredLessonsToJoin] = useState([]);
  const [searchValue, setSearchValue] = useState("");
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const userEmail = getCookie("userEmail");

  useEffect(() => {
    if (!getCookie("userEmail")) {
      navigate("/");
    }
    const fetchInProgress = async () => {
      const response = await axios.post(
        `${baseURL}/get_in_progress_assignments/`,
        { student_username: userEmail }
      );
      setLessonsInProgress(response.data.in_progress_assignments);
      console.log(response.data);
    };
    const fetchCreated = async () => {
      const response = await axios.post(
        `${baseURL}/get_all_created_assignments/`,
        { creator_username: userEmail }
      );
      setPastCreatedLessons(response.data.assignment_list);
    };
    const fetchJoined = async () => {
      const response = await axios.post(
        `${baseURL}/get_all_assigned_assignments/`,
        { student_username: userEmail }
      );
      setPastJoinedLessons(response.data.assignment_list);
    };
    const fetchPublic = async () => {
      const response = await axios.post(
        `${baseURL}/get_all_unjoined_public_assignments/`,
        { num_assignments_to_retrieve: 10, username: userEmail }
      );
      setLessonsToJoin(response.data.assignment_list);
    };
    const fetchAllData = async () => {
      try {
        await Promise.all([
          fetchInProgress(),
          fetchCreated(),
          fetchJoined(),
          fetchPublic(),
        ]);
      } catch (error) {
        console.log(error);
      } finally {
        setLoading(false);
      }
    };
    fetchAllData();
  }, []);

  const joinAssignment = async (assignmentId) => {
    setLoading(true);
    const response = await axios.post(`${baseURL}/join_assignment/`, {
      assignment_id: assignmentId,
      student_username: userEmail,
    });
    setLoading(false);
    if ("status" in response.data && response.data.status === "Error.") {
      console.log(response.data.message);
    } else {
      navigate("/lesson", {
        state: {
          assignmentId: assignmentId,
          studentUsername: userEmail,
          attemptNumber: 1,
        },
      });
    }
  };

  const handleSearch = (query) => {
    setSearchValue(query);
    console.log("Search query:", query);
  };

  const filterLessons = (lessons) => {
    return lessons.filter((lesson) =>
      lesson.assignment_title.toLowerCase().includes(searchValue)
    );
  };

  const copyToClipboard = (assignmentId) => {
    copy(assignmentId);
  };

  const copy = (text) => {
    // Create a hidden input
    const input = document.createElement("input");
    input.setAttribute("value", text);
    document.body.appendChild(input);

    // Select the text and copy it to the clipboard
    input.select();
    document.execCommand("copy");

    // Remove the input from the DOM
    document.body.removeChild(input);

    // Provide feedback to the user
    setCopied(true);
    setTimeout(() => setCopied(false), 1000); // Clear message after 1 second
  };

  useEffect(() => {
    setFilteredInProgressLessons(filterLessons(lessonsInProgress));
    setFilteredPastCreatedLessons(filterLessons(pastCreatedLessons));
    setFilteredPastJoinedLessons(filterLessons(pastJoinedLessons));
    setFilteredLessonsToJoin(filterLessons(lessonsToJoin));
  }, [
    searchValue,
    lessonsInProgress,
    pastCreatedLessons,
    pastJoinedLessons,
    lessonsToJoin,
  ]);

  return (
    <div>
      <Navbar onSearch={handleSearch} />
      <ProfileHeader showOptions={true} />
      <div className="home-page">
        <div className="home-left-side">
          <div className="in-progress-section">
            <div className="section-header">
              Continue Lessons ({filteredInProgressLessons.length})
            </div>
            {filteredInProgressLessons.length > 0 ? (
              <div className="in-progress-lessons">
                {filteredInProgressLessons.map((lesson, index) => (
                  <div
                    className="in-progress-box"
                    key={index}
                    onClick={() =>
                      navigate("/lesson", {
                        state: {
                          assignmentId: lesson.assignment_id,
                          studentUsername: userEmail,
                          attemptNumber: lesson.student_attempt,
                        },
                      })
                    }
                  >
                    <h3>{lesson.assignment_title}</h3>
                    <p>Created by: {lesson.creator_name}</p>
                    <div className="progress-container">
                      <div
                        className="progress-bar"
                        style={{ width: `${lesson.progress_bar}%` }}
                      ></div>
                      <span className="progress-percent">
                        {lesson.progress_bar}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-lessons">You have no lessons in progress</p>
            )}
          </div>

          {/* Past Lessons Section */}
          <div className="lessons-section">
            <div className="section-header">Past Lessons</div>
            <div className="toggle-buttons">
              <button
                className={viewCreated ? "active created" : "created"}
                onClick={() => setViewCreated(true)}
              >
                Created
              </button>
              <button
                className={!viewCreated ? "active joined" : "joined"}
                onClick={() => setViewCreated(false)}
              >
                Joined
              </button>
            </div>
            {(viewCreated
              ? filteredPastCreatedLessons
              : filteredPastJoinedLessons
            ).length > 0 ? (
              <div className="past-lessons-container">
                <table className="lesson-table">
                  <thead>
                    <tr>
                      <th>Lesson Name</th>
                      <th>{viewCreated ? "Joined Users" : "Attempt"}</th>
                      <th>Last Updated</th>
                      <th>{viewCreated ? "View Attempts" : "View Lesson"}</th>
                      <th>Lesson ID</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(viewCreated
                      ? filteredPastCreatedLessons
                      : filteredPastJoinedLessons
                    ).map((lesson, index) => (
                      <tr key={index}>
                        <td>{lesson.assignment_title}</td>
                        <td>
                          {viewCreated
                            ? lesson.num_students
                            : lesson.student_attempt}
                        </td>
                        <td>{lesson.last_updated}</td>
                        <td>
                          {viewCreated ? (
                            <button
                              className="join-button"
                              onClick={() =>
                                navigate("/results", {
                                  state: {
                                    assignmentId: lesson.assignment_id,
                                    assignmentTitle: lesson.assignment_title,
                                  },
                                })
                              }
                            >
                              View Attempts
                            </button>
                          ) : (
                            <button
                              className="join-button"
                              onClick={() =>
                                navigate("/lesson", {
                                  state: {
                                    assignmentId: lesson.assignment_id,
                                    studentUsername: userEmail,
                                    attemptNumber: lesson.student_attempt,
                                  },
                                })
                              }
                            >
                              Chat
                            </button>
                          )}
                        </td>
                        <td>
                          <button
                            className="join-button"
                            onClick={() =>
                              copyToClipboard(lesson.assignment_id)
                            }
                          >
                            Copy
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="no-lessons">You have no past lessons to view</p>
            )}
          </div>
        </div>

        {/* Lessons to Join Section */}
        <div className="home-right-side">
          <div className="public-lessons">
            <div className="section-header">
              Public Lessons to Join ({filteredLessonsToJoin.length})
            </div>
            {filteredLessonsToJoin.length > 0 ? (
              <div className="public-lessons-container">
                {filteredLessonsToJoin.map((lesson, index) => (
                  <div className="public-lessons-box" key={index}>
                    <h3>{lesson.assignment_title}</h3>
                    <p>Created by: {lesson.creator_name}</p>
                    <button
                      className="join-button"
                      onClick={() => joinAssignment(lesson.assignment_id)}
                    >
                      Join {lesson.num_students} students →
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-lessons">You have no lessons to join</p>
            )}
          </div>
        </div>
      </div>
      {loading && <LoadingSpinner />}
      {copied && (
        <div className="loading-overlay">
          <div className="finished-loading-container">
            <div className="loading-subtext">
              Lesson ID Copied to Clipboard!
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default HomePage;
