import React, { useState, useEffect } from "react";
import "../css/CreateLessonPage.css";
import Navbar from "../components/Navbar";
import ProfileHeader from "../components/ProfileHeader";
import { useLocation, useNavigate } from "react-router-dom";
import axios from "axios";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorOverlay from "../components/ErrorOverlay";
import { getCookie, baseURL } from "../functions/Funcs";
import Tooltip from "../components/Tooltip";
axios.defaults.timeout = 1000000;

const lessonMap = {
  "5 mins ~ 10 mins": 10,
  "10 mins ~ 20 mins": 20,
  "20 mins ~ 30 mins": 30,
  "30 mins ~ 1 hour": 60,
};

function CreateLessonPage() {
  const location = useLocation();
  // eslint-disable-next-line
  const data = location.state || {};
  const navigate = useNavigate();
  const [answer, setAnswer] = useState("");
  const [formData, setFormData] = useState({
    lessonName: "",
    taskDescription: "",
    lessonLength: "5 mins ~ 10 mins",
    answerVisible: "Yes",
    privacy: "public",
    firstPrompt: "",
  });
  const [uploading, setUploading] = useState("Not started");
  const [assignmentId, setAssignmentId] = useState("");
  const [error, setError] = useState(null);
  const userEmail = getCookie("userEmail");

  useEffect(() => {
    if (!getCookie("userEmail")) {
      navigate("/");
    }
    if (!data) {
      navigate("/create-lesson");
    } else {
      if ("answer" in data) {
        setAnswer(data.answer);
      }
      if ("lesson" in data) {
        setAnswer(data.lesson);
      }
      setFormData((prevFormData) => ({
        ...prevFormData,
        ...(data.firstPrompt && { firstPrompt: data.firstPrompt }),
        ...(data.taskDescription && { taskDescription: data.taskDescription }),
        ...(data.title && { lessonName: data.title }),
      }));
    }
  }, [data, navigate]);

  const handleSubmit = async (e) => {
    setUploading("Started");
    e.preventDefault();
    const uploadData = {
      creator_username: userEmail,
      assignment_title: formData.lessonName,
      topic: formData.taskDescription,
      lesson: answer,
      first_prompt: formData.firstPrompt,
      lesson_length: lessonMap[formData.lessonLength],
      hide_assignment_answer: formData.answerVisible === "Yes" ? true : false,
      private_assignment: formData.privacy === "private" ? true : false,
    };
    try {
      const response = await axios.post(
        `${baseURL}/create_assignment/`,
        uploadData
      );
      if ("status" in response.data && response.data.status === "Error.") {
        setError(response.data);
      } else {
        setUploading("Finished");
        console.log(response.data);
        setAssignmentId(response.data.assignment_id);
      }
    } catch (error) {
      console.error("Error in aiAugmentLessonContents:", error.message);
      setError(error);
    }
  };

  const goBack = (e) => {
    navigate("/create-lesson", {
      state: {
        lesson: answer,
      },
    });
  };

  const goHome = (e) => {
    navigate("/home");
  };

  const showDemo = () => {
    navigate("/demo", {
      state: {
        topic: formData.lessonName,
        question: formData.taskDescription,
        answer: answer,
        lessonLength: formData.lessonLength,
        answerVisible: formData.answerVisible,
        privacy: formData.privacy,
        firstPrompt: formData.firstPrompt,
      },
    });
  };

  return (
    <div>
      <Navbar />
      <ProfileHeader />

      {/* Create lesson container */}
      <div className="create-lesson-container">
        <h2>Finalize Lesson</h2>

        <form className="create-lesson-form" onSubmit={handleSubmit}>
          <div className="form-columns">
            {/* Left column - form fields */}
            <div className="left-column">
              <div className="form-group">
                <label>
                  Lesson Name{" "}
                  <Tooltip text="Name to be displayed when selecting a lesson" />
                </label>
                <input
                  type="text"
                  name="lessonName"
                  placeholder="e.g. Photosynthesis and Cellular Respiration"
                  required
                  autoComplete="off"
                  value={formData.lessonName}
                  onChange={(e) =>
                    setFormData({ ...formData, lessonName: e.target.value })
                  }
                />
              </div>

              <div className="form-group">
                <label>
                  Task Description{" "}
                  <Tooltip text="Describe the purpose/goal of the lesson for students" />
                </label>
                <textarea
                  name="taskDescription"
                  placeholder="e.g. Explain the processes by which plants convert sunlight into energy..."
                  required
                  value={formData.taskDescription}
                  style={{ height: "10vh" }}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      taskDescription: e.target.value,
                    })
                  }
                />
              </div>
              <div className="form-group">
                <label>
                  First Prompt{" "}
                  <Tooltip text="The first question to be asked to students to begin their learning journey" />
                </label>
                <input
                  type="text"
                  name="firstPrompt"
                  placeholder="e.g. What is photosynthesis?"
                  autoComplete="off"
                  required
                  defaultValue={formData.firstPrompt}
                  onChange={(e) =>
                    setFormData({ ...formData, firstPrompt: e.target.value })
                  }
                />
              </div>
            </div>

            {/* Right column - file upload and buttons */}
            <div className="right-column">
              <div className="form-group">
                <label>
                  Lesson Length{" "}
                  <Tooltip text="Docere will ask more/less questions based upon your intended lesson length" />
                </label>
                <select
                  name="lessonLength"
                  value={formData.lessonLength}
                  onChange={(e) =>
                    setFormData({ ...formData, lessonLength: e.target.value })
                  }
                >
                  <option>5 mins ~ 10 mins</option>
                  <option>10 mins ~ 20 mins</option>
                  <option>20 mins ~ 30 mins</option>
                  <option>30 mins ~ 1 hour</option>
                </select>
              </div>

              <div className="form-group">
                <label>
                  Answer Visible After Completion{" "}
                  <Tooltip text="Whether or not students can see the answer after completing a lesson" />
                </label>
                <select
                  name="answerVisible"
                  value={formData.answerVisible}
                  onChange={(e) =>
                    setFormData({ ...formData, answerVisible: e.target.value })
                  }
                >
                  <option>Yes</option>
                  <option>No</option>
                </select>
              </div>
              <div className="form-group">
                <label>
                  Privacy{" "}
                  <Tooltip text="Whether the lesson is avaliable to everyone or just certain students" />
                </label>
                <div className="privacy-options">
                  <label>
                    <input
                      type="radio"
                      name="privacy"
                      value="public"
                      checked={formData.privacy === "public"}
                      onChange={(e) =>
                        setFormData({ ...formData, privacy: e.target.value })
                      }
                    />{" "}
                    Public (anyone can join)
                  </label>
                  {/* <label>
                    <input
                      type="radio"
                      name="privacy"
                      value="class"
                      checked={formData.privacy === "class"}
                      onChange={(e) =>
                        setFormData({ ...formData, privacy: e.target.value })
                      }
                    />{" "}
                    Students in your class
                  </label> */}
                  <label>
                    <input
                      type="radio"
                      name="privacy"
                      value="private"
                      checked={formData.privacy === "private"}
                      onChange={(e) =>
                        setFormData({ ...formData, privacy: e.target.value })
                      }
                    />{" "}
                    Private (only you)
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div className="form-buttons">
            <button type="button" className="cancel-btn" onClick={showDemo}>
              <img src="images/sparkle.png" alt="Sparkle" height={"20px"} />{" "}
              &nbsp; Watch Demo
            </button>
            <button type="button" className="cancel-btn" onClick={goBack}>
              Back
            </button>
            <button type="submit" className="next-btn">
              Submit
            </button>
          </div>
        </form>
      </div>
      {uploading === "Started" && <LoadingSpinner />}
      {uploading === "Finished" && (
        <div className="loading-overlay">
          <div className="finished-loading-container">
            <div className="loading-message">Lesson Uploaded!</div>
            <div className="loading-subtext">
              Your lesson ID is {assignmentId}
            </div>
            <button type="button" className="overlay-home-btn" onClick={goHome}>
              Go Home
            </button>
          </div>
        </div>
      )}
      {error && <ErrorOverlay error={error} />}
    </div>
  );
}

export default CreateLessonPage;
