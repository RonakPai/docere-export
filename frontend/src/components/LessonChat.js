import React, { useEffect, useState, useRef } from "react";
import "../css/LessonChat.css";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { getCookie, baseURL } from "../functions/Funcs";
axios.defaults.timeout = 1000000;

const LessonChat = ({
  studentUsername,
  attemptNumber,
  assignment,
  viewAnalysis,
}) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: assignment.first_prompt,
      role: "model",
    },
  ]);
  const [progress, setProgress] = useState(0); // Variable to track progress, change as needed
  const [messageAdding, setMessageAdding] = useState(false);
  const [lessonDone, setLessonDone] = useState(false);
  const inputRef = useRef(null);
  const userEmail = getCookie("userEmail");

  useEffect(() => {
    const fetchData = async () => {
      const response = await axios.post(`${baseURL}/get_assignment_progress/`, {
        assignment_id: assignment.assignment_id,
        student_username: studentUsername,
        student_attempt: attemptNumber,
      });
      setProgress(response.data.progress_bar);
      setLessonDone(response.data.progress_bar === 100);
      if (response.data.progress_bar !== 0) {
        const oldMessages = JSON.parse(response.data.history_as_string);
        //eslint-disable-next-line
        oldMessages.map((item, index) => {
          // Ignore first and second messages
          if (index > 1) {
            setMessages((prevMessages) => [
              ...prevMessages,
              { id: prevMessages.length + 1, text: item.text, role: item.role },
            ]);
          }
        });
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    const chatContent = document.querySelector(".lesson-chat-content");
    chatContent.scrollTop = chatContent.scrollHeight;
  }, [messages]);

  const addMessage = async (newMessage) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { id: prevMessages.length + 1, text: newMessage, role: "user" },
    ]);
    setMessageAdding(true);
    const questionData = {
      assignment_id: assignment.assignment_id,
      student_username: studentUsername,
      student_answer: newMessage,
      student_attempt: attemptNumber,
    };
    const response = await axios.post(
      `${baseURL}/get_next_question/`,
      questionData
    );
    setProgress(response.data.progress_bar);
    setLessonDone(response.data.lesson_completed);
    setMessages((prevMessages) => [
      ...prevMessages,
      {
        id: prevMessages.length + 1,
        text: response.data.next_question,
        role: "model",
      },
    ]);

    setMessageAdding(false);
    setTimeout(() => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }, 10);
  };

  const getHelp = () => {
    if (!messageAdding) {
      addMessage("Hm, I'm not sure, could you give me a hint?");
    }
  };

  const clickViewAnalysis = () => {
    viewAnalysis(studentUsername, attemptNumber);
  };

  return (
    <div className="lesson-chat-container">
      <div className="progress-container">
        <div className="progress-bar" style={{ width: `${progress}%` }}></div>
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
        {messageAdding && (
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
      </div>

      {!lessonDone && userEmail === studentUsername && (
        <div className="input-section">
          <div className="get-hint" onClick={getHelp}>
            Need A Hint?
          </div>
          <div className="lesson-chat-input">
            <textarea
              ref={inputRef}
              placeholder="Start typing..."
              rows={4} // Start with one line
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault(); // Prevent newline
                  addMessage(e.target.value);
                  inputRef.current.value = "";
                }
              }}
              disabled={messageAdding}
              style={{
                maxHeight: "80px", // Limit height to four lines
                overflow: "auto",
                resize: "none",
              }}
            />
          </div>
        </div>
      )}
      {lessonDone && (
        <div class="lesson-complete">
          <div className="lesson-complete-title">Lesson Complete 🎉</div>
          <div className="lesson-complete-text">
            Docere will analyze your answers to "{assignment.assignment_title}"
            and prepare a detailed AI-generated report, along with an adapated
            lesson targeting your weaknesses to optimize your learning
          </div>
          <button className="view-analysis" onClick={clickViewAnalysis}>
            View Analysis
          </button>
        </div>
      )}
    </div>
  );
};

export default LessonChat;
