import React, { useRef, useState, useEffect } from "react";
import "../css/LessonAnalysis.css"; // Assuming you will style the component here
import "../css/LessonChat.css";
import ReactMarkdown from "react-markdown";

const LessonAnalysis = ({ report }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const containerRef = useRef(null);

  const categories = Object.keys(report);
  const totalPages = categories.length;

  useEffect(() => {
    const lessonSummaryIndex = categories.indexOf("Lesson Summary");
    if (lessonSummaryIndex !== -1) {
      setCurrentPage(lessonSummaryIndex);
    }
  }, []);

  const handleNextPage = () => {
    setCurrentPage((prevPage) => (prevPage + 1) % totalPages);
    if (containerRef.current) {
      containerRef.current.scrollTo(0, 0);
    }
  };

  const handlePrevPage = () => {
    setCurrentPage((prevPage) => (prevPage - 1 + totalPages) % totalPages);
    if (containerRef.current) {
      containerRef.current.scrollTo(0, 0);
    }
  };

  return (
    <div className="lesson-chat-container">
      <h2>Analysis</h2>

      <div className="analysis-content" ref={containerRef}>
        <div className="what-you-wrote">
          <h3>{categories[currentPage]}</h3>
          <div className="user-response">
            {Array.isArray(report[categories[currentPage]]) ? (
              report[categories[currentPage]].map((item, index) => (
                <ul key={index}>
                  <li>
                    <ReactMarkdown>{item}</ReactMarkdown>
                  </li>
                </ul>
              ))
            ) : (
              <ReactMarkdown>{report[categories[currentPage]]}</ReactMarkdown>
            )}
          </div>
        </div>

        {/* Pagination Controls */}
        <div className="pagination-controls">
          <button className="prev-button" onClick={handlePrevPage}>
            &lt;
          </button>
          <div className="page-indicators">
            {Array.from({ length: totalPages }).map((_, index) => (
              <span
                key={index}
                className={`indicator ${index === currentPage ? "active" : ""}`}
              >
                ●
              </span>
            ))}
          </div>
          <button className="next-button" onClick={handleNextPage}>
            &gt;
          </button>
        </div>
      </div>
    </div>
  );
};

export default LessonAnalysis;
