import { React, useEffect, useState } from "react";
import "../css/LessonPage.css";
import Navbar from "../components/Navbar";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { getCookie, baseURL } from "../functions/Funcs";
axios.defaults.timeout = 1000000;

function DemoPage() {
  const location = useLocation();
  const navigate = useNavigate();
  // eslint-disable-next-line
  const data = location.state || {};
  const [messages, setMessages] = useState([]);
  const [progress, setProgress] = useState(0);
  const [finished, setFinished] = useState(false);
  const [demoState, setDemoState] = useState("student");

  const userEmail = getCookie("userEmail");

  const addMessage = (message, user) => {
    setMessages((prevMessages) => {
      return [
        ...prevMessages,
        { id: prevMessages.length + 1, text: message, role: user },
      ];
    });
  };

  const getAnswer = async (lastMessage) => {
    const response = await axios.post(`${baseURL}/get_ai_presenter_answer/`, {
      username: userEmail,
      topic: data.topic,
      lesson: data.answer,
      question: data.question,
      next_question: lastMessage,
    });
    addMessage(response.data, "user");
    setDemoState("model");
  };

  const getQuestion = async (lastMessage) => {
    const response = await axios.post(
      `${baseURL}/get_next_question_for_lesson_simulation/`,
      {
        topic: data.topic,
        lesson: data.answer,
        question: data.question,
        student_answer: lastMessage,
        history_as_string: JSON.stringify(messages),
        previous_progress: progress,
      }
    );
    setFinished(response.data.lesson_completed);
    setProgress(response.data.progress_bar);
    addMessage(response.data.next_question, "model");
    setDemoState("student");
  };

  const goBack = () => {
    navigate("/finalize-lesson", {
      state: data,
    });
  };

  useEffect(() => {
    if (!getCookie("userName")) {
      navigate("/");
    }
    if ("topic" in data === false) {
      navigate("/home");
    }
    addMessage(data.firstPrompt, "model");
  }, [data, navigate]);

  useEffect(() => {
    if (finished) {
      return;
    }
    if (messages.length === 0) {
      return;
    }
    if (demoState === "model") {
      setDemoState("in-progress-model");
      getQuestion(messages[messages.length - 1].text);
    } else if (demoState === "student") {
      setDemoState("in-progress-student");
      getAnswer(messages[messages.length - 1].text);
    }
    // eslint-disable-next-line
  }, [messages, finished, getAnswer, getQuestion]);

  useEffect(() => {
    const chatContent = document.querySelector(".lesson-chat-content");
    chatContent.scrollTop = chatContent.scrollHeight;
  }, [messages]);

  return (
    <div>
      <Navbar />
      <div className="lesson-page">
        <div className="question-column">
          <h1>{data.topic}</h1>
          <br />
          <div className="created-by">Creator: {getCookie("userName")}</div>
          <div className="description">{data.question}</div>
          <button type="button" className="start-button" onClick={goBack}>
            Back to Lesson Creation
          </button>
        </div>
        <div className="lesson-chat-container">
          <div className="progress-container">
            <div
              className="progress-bar"
              style={{ width: `${progress}%` }}
            ></div>
            <span className="progress-percent">{progress}%</span>
          </div>
          <div className="lesson-chat-content">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.role}`}>
                {message.role === "model" && (
                  <img
                    src="/images/chat-logo.png"
                    alt="Docere Logo"
                    className="message-logo"
                  />
                )}
                <ReactMarkdown>{message.text}</ReactMarkdown>
              </div>
            ))}
            {demoState === "in-progress-model" && (
              <div className="message model">
                <img
                  src="/images/chat-logo.png"
                  alt="Docere Logo"
                  className="message-logo"
                />
                <div className="loading-dots">
                  <span>. &thinsp;</span>
                  <span>. &thinsp;</span>
                  <span>. &thinsp;</span>
                </div>
              </div>
            )}
            {demoState === "in-progress-student" && (
              <div className="message user">
                <div className="loading-dots">
                  <span>. &thinsp;</span>
                  <span>. &thinsp;</span>
                  <span>. &thinsp;</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DemoPage;
