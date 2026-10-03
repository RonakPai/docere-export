'''
GenAI Presenter. Use Cases TBD.

Use Case ideas:
1. Demo simulation of the platform (although this could be hardcoded, but GenAI-powered simulation could be cool).
2. A teacher can setup an assignment (a topic and lesson) and watch our GenAI agent complete the assignment.
3. A student can watch a GenAI agent complete the assignment (after its deadline or something) to understand the concept better.
4. A tutor that the student can just ask questions to about the lesson (accessible after assignment deadline).
'''

from llm_classes import GeminiLLM
import rds_management

def ai_presenter_response_helper(assignment_id: str,
                                 topic: str,
                                 question: str,
                                 lesson: str,
                                 question_for_ai_presenter: str,
                                 correct: bool = True):
    
    if topic != "" and lesson != "":
        if question != "":
            topic = "**TOPIC:**\n{}\n\n**QUESTION(S):**\n{}".format(topic, question)
        return ai_presenter_response(topic=topic,
                                     lesson=lesson,
                                     next_question=question_for_ai_presenter,
                                     correct=correct)
    else: # use assignment ID for topic and lesson retrieval
        assignment_info = rds_management.get_assignment_info(assignment_id=assignment_id)
        topic = "**TOPIC:**\n{}\n\n**QUESTION(S):**\n{}".format(assignment_info['topic'], assignment_info['question'])
        return ai_presenter_response(topic=topic,
                                     lesson=assignment_info['lesson'],
                                     next_question=question_for_ai_presenter,
                                     correct=correct)

def ai_presenter_response(topic: str,
                          lesson: str,
                          next_question: str,
                          correct: bool = True):
    
    answer_correctness = "CORRECT" if correct else "INCORRECT"

    ai_presenter_system_instruction = """You are a student presenting a lesson to the class today. \
This presentation will follow a question+answer format in which you will be asked suggestive, guiding question by the teacher \
and you will answer the question; this back-and-forth will repeat until you have covered ALL information that is part of the lesson.

You will teach a lesson discussing the following topic/question: '{topic}'

Here is the entire lesson that you are to teach about this topic/question by the end of the presentation (treat this as ground truth information): '{lesson}'

You will be given the questions from the teacher and expected to respond with a(n) {answer_correctness}, CONCISE BUT COMPLETE answer.
Phrase your answers conversationally, as they would be said aloud.
Stick to SOLELY discussing information in the lesson you are to teach, do NOT discuss tangential information.

NOTE: Do not use any non-alphanumeric character (like emojis).
    """.format(topic=topic, lesson=lesson, answer_correctness=answer_correctness)
    
    ai_presenter_agent = GeminiLLM(temperature=0.2,
                                   top_p=0.1,
                                   system_instruction=ai_presenter_system_instruction,)
    return ai_presenter_agent.generate_content(next_question).text.strip()