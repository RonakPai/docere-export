import React, { useState, useEffect } from "react";
import "../css/CreateLessonPage.css";
import Navbar from "../components/Navbar";
import mammoth from "mammoth";
import * as pdfjsLib from "pdfjs-dist/build/pdf";
import { useNavigate, useLocation } from "react-router-dom";
import ProfileHeader from "../components/ProfileHeader";
import axios from "axios";
import LoadingSpinner from "../components/LoadingSpinner";
import Tooltip from "../components/Tooltip";
import { getCookie, baseURL } from "../functions/Funcs";
axios.defaults.timeout = 1000000;

pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

function CreateLessonPage() {
  const [lesson, setLesson] = useState("");
  const [fileChanging, setFileChanging] = useState(false);
  const [fileNames, setFileNames] = useState([]);
  const [loading, setLoading] = useState(false);

  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    if (!getCookie("userName")) {
      navigate("/");
    }
    if (location.state) {
      setLesson(location.state.lesson);
    }
  }, [location.state]);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    setFileChanging(true);
    setLoading(true);
    let fileContents = "";
    if (!file) return;

    const fileExtension = file.name.split(".").pop().toLowerCase();

    if (fileExtension === "txt") {
      // Handle text files
      const reader = new FileReader();
      reader.onload = () => {
        fileContents += "\n" + reader.result;
        setFileChanging(false);
      };
      reader.readAsText(file);
      setFileNames([...fileNames, file.name]);
    } else if (fileExtension === "docx") {
      // Handle DOCX files using mammoth
      const arrayBuffer = await file.arrayBuffer();
      mammoth
        .extractRawText({ arrayBuffer: arrayBuffer })
        .then((result) => {
          fileContents += "\n" + result.value; // The raw text content of the DOCX file
          setFileChanging(false);
        })
        .catch((err) => console.error("Error processing DOCX file:", err));
      setFileNames([...fileNames, file.name]);
    } else if (fileExtension === "pdf") {
      // Handle PDF files using pdfjs-dist
      const reader = new FileReader();
      reader.onload = async function () {
        const typedArray = new Uint8Array(reader.result);
        const pdf = await pdfjsLib.getDocument(typedArray).promise;
        let textContent = "";
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const text = await page.getTextContent();
          // eslint-disable-next-line
          text.items.forEach((item) => {
            textContent += item.str + " ";
          });
        }
        fileContents += "\n" + textContent;
        setFileChanging(false);
        setFileNames([...fileNames, file.name]);
      };
      reader.readAsArrayBuffer(file);
    } else {
      console.log(
        "Unsupported file type. Please upload a .pdf, .docx, or .txt file."
      );
      setFileChanging(false);
    }
    while (fileContents === "") {
      await new Promise((r) => setTimeout(r, 10));
    }
    fileContents += "\n" + lesson;
    const response = await axios.post(
      `${baseURL}/ai_augment_uploaded_lesson_contents/`,
      {
        lesson: fileContents,
      }
    );
    setLesson(response.data);
    setLoading(false);
  };

  const aiAugmentLessonContents = async (data) => {
    try {
      const response = await axios.post(
        `${baseURL}/generate_assignment_contents/`,
        data
      );
      return response.data;
    } catch (error) {
      console.error("Error in aiAugmentLessonContents:", error.message);
      throw error;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    while (fileChanging) {
      await new Promise((resolve) => setTimeout(resolve, 10));
    }

    try {
      let result = await aiAugmentLessonContents({ lesson_contents: lesson });
      setLoading(false);

      navigate("/finalize-lesson", {
        state: {
          answer: lesson,
          firstPrompt: result.first_prompt,
          taskDescription: result.task_description,
          title: result.title,
        },
      });
    } catch (error) {
      console.error("Error during form submission:", error.message);
    }
  };

  return (
    <div>
      <Navbar />
      <ProfileHeader />

      <div className="create-lesson-container">
        {/* Create lesson container */}
        <h2>Create Lesson</h2>

        <form className="create-lesson-form" onSubmit={handleSubmit}>
          <div className="form-columns">
            {/* Left column - form fields */}
            <div className="left-column">
              <div className="form-group">
                <label>
                  Lesson Content{" "}
                  <Tooltip text="Type your lesson contents (bullet points, paragraphs, textbook passages, etc.) here" />
                </label>
                <textarea
                  placeholder="Begin creating your lesson plan..."
                  required
                  style={{ height: "43vh" }}
                  defaultValue={lesson}
                  onChange={(e) => setLesson(e.target.value)}
                />
              </div>
            </div>

            {/* Right column - file upload and buttons */}
            <div className="right-column">
              <div className="form-group">
                <label>
                  Upload Files{" "}
                  <Tooltip text="Upload files with your lesson contents (bullet points, paragraphs, textbook passages, etc.) here" />
                </label>
                <div
                  className="file-upload-box"
                  onClick={() => document.getElementById("file-input").click()}
                >
                  <input
                    id="file-input"
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.docx,.txt"
                    style={{ display: "none" }}
                  />
                  <img src="images/upload.png" alt="Docere Logo" />
                  <p>
                    (Optional) Drag file here or select a file <br />
                    Accepted file types: .pdf, .docx, .txt
                  </p>
                  {fileNames.length > 0 && (
                    <div>
                      <div className="uploaded-files-label">Uploaded Files</div>
                      {fileNames.map((name, index) => (
                        <div className="uploaded-files" key={index}>
                          {name}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="form-buttons">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => navigate("/home")}
                >
                  Cancel
                </button>
                <button type="submit" className="next-btn">
                  Next
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
      {/* Loading Overlay */}
      {loading && <LoadingSpinner />}
    </div>
  );
}

export default CreateLessonPage;
