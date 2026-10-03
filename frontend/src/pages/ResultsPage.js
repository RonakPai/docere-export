import React, { useEffect, useState } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";
import LoadingSpinner from "../components/LoadingSpinner";
import Navbar from "../components/Navbar";
import ProfileHeader from "../components/ProfileHeader";
import "../css/ResultsPage.css";
import { baseURL, getCookie } from "../functions/Funcs";
axios.defaults.timeout = 1000000;

function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const data = location.state || {};
  const [loading, setLoading] = useState(true);
  const [students, setStudents] = useState([]);

  useEffect(() => {
    if (!getCookie("userName")) {
      navigate("/");
    }
    if ("assignmentId" in data === false) {
      navigate("/home");
    }
    const getData = async () => {
      const response = await axios.post(`${baseURL}/get_all_students/`, {
        assignment_id: data.assignmentId,
      });
      setStudents(response.data.student_list);
      setLoading(false);
    };

    getData();
  });

  return (
    <div>
      <Navbar />
      <ProfileHeader />
      <div className="results-container">
        <h2>"{data.assignmentTitle}" Attempts</h2>
        <table className="results-table">
          <thead>
            <tr>
              <th>Student Name</th>
              <th>Attempt</th>
              <th>Last Updated</th>
              <th>View Lesson</th>
            </tr>
          </thead>
          <tbody>
            {" "}
            {students.map((student, index) => (
              <tr key={index}>
                <td>{student.student_name}</td>
                <td>{student.student_attempt}</td>
                <td>{student.last_updated}</td>
                <td>
                  <button
                    className="join-button"
                    onClick={() =>
                      navigate("/lesson", {
                        state: {
                          assignmentId: data.assignmentId,
                          studentUsername: student.student_username,
                          attemptNumber: student.student_attempt,
                        },
                      })
                    }
                  >
                    View Lesson
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {loading && <LoadingSpinner />}
    </div>
  );
}

export default ResultsPage;
