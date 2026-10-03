import "../css/LessonStart.css";

function LessonStart() {
  return (
    <div className="how-it-works">
      <div className="how-it-works-title">How It Works</div>
      <div className="explain-row">
        <div className="explain-bubble">
          <h3>Learn</h3>
          <p>
            Docere will automatically generate prompts related to the uploaded
            lesson plan to facilitate a cohesive understanding of the content
          </p>
        </div>
        <div className="explain-bubble">
          <h3>Analyze</h3>
          <p>
            Docere will analyze your answers to prepare a detailed AI-generated
            report, personalizing your strengths and weaknesses
          </p>
        </div>
        <div className="explain-bubble">
          <h3>Understand</h3>
          <p>
            Docere will adapt a revised lesson based upon your weaknesses to
            optimize your learning in future iterations of the lesson
          </p>
        </div>
      </div>
    </div>
  );
}

export default LessonStart;
