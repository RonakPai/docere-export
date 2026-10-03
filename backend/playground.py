# import statements

import vertexai

import keys

from vertexai.generative_models import GenerativeModel, GenerationConfig, HarmCategory, HarmBlockThreshold
from google.oauth2 import service_account

class GeminiLLM:

    def __init__(self,
                temperature: float = None,
                top_p: float = None,
                system_instruction: str = None):
        
        credentials_json = {
        "type": "service_account",
        "project_id": keys.VERTEX_AI_PROJECT_ID,
        "private_key_id": keys.VERTEX_AI_PRIVATE_KEY_ID,
        "private_key": keys.VERTEX_AI_PRIVATE_KEY,
        "client_email": keys.VERTEX_AI_CLIENT_EMAIL,
        "client_id": keys.VERTEX_AI_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": keys.VERTEX_AI_CLIENT_X509_CERT_URL,
        "universe_domain": "googleapis.com"
        }
        self.credentials = service_account.Credentials.from_service_account_info(credentials_json)
        self.vertex_ai_location = "us-east1"
        vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)

        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        self.llm_config = GenerationConfig(temperature=temperature, top_p=top_p)
        self.system_instruction = system_instruction 
        self.llm = GenerativeModel(model_name="gemini-1.5-pro", 
                                   system_instruction=self.system_instruction,
                                   generation_config=self.llm_config, 
                                   safety_settings=self.safety_settings,)
        self.chat = self.llm.start_chat()

    def switch_vertex_ai_location(self,):
        if self.vertex_ai_location == "us_east1":
            self.vertex_ai_location = "us-central1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)
        elif self.vertex_ai_location == "us-central1":
            self.vertex_ai_location = "us-west1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)
        else:
            self.vertex_ai_location = "us-east1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)

    def generate_content(self,
                         prompt: str,):
        try:
            response = self.llm.generate_content(prompt)
        except Exception as e:
            try:
                self.switch_vertex_ai_location()
                self.llm = GenerativeModel(model_name="gemini-1.5-pro", generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                response = self.llm.generate_content(prompt)
            except Exception as e:
                try:
                    self.switch_vertex_ai_location()
                    self.llm = GenerativeModel(model_name="gemini-1.5-pro", generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    response = self.llm.generate_content(prompt)
                except Exception as e:
                    self.switch_vertex_ai_location()
                    self.llm = GenerativeModel(model_name="gemini-1.5-pro", generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    raise(e)
        # print("[GEMINI 1.5 PRO]\nINPUT: {} CHARACTERS.\nOUTPUT: {} CHARACTERS.".format(self.llm.count_tokens(prompt).total_billable_characters, self.llm.count_tokens(response.text).total_billable_characters))
        return response
    
    def send_message(self,
                     prompt: str,):
        response = self.chat.send_message(prompt)
        # print("[GEMINI 1.5 PRO]\nINPUT: {} CHARACTERS.\nOUTPUT: {} CHARACTERS.".format(self.llm.count_tokens(prompt).total_billable_characters, self.llm.count_tokens(response.text).total_billable_characters))
        return response
    
    def set_history(self,
                    history):
        self.chat = self.llm.start_chat(history=history)
    
    def get_history(self):
        return self.chat.history
    
    def generate_final_report(self,
                              lesson: str,):
        prompt = """\
You are observing a lesson being presented by a student;
This presentation will follow a question+answer format in which the teacher will ask suggestive, guiding questions to the student \
and the student will answer the teacher's questions. This back-and-forth will repeat until the student has covered ALL information that is part of the lesson that they are to teach.

Here is the entire lesson that the student is to teach by the end of their presentation: {lesson}

Your task is to draft a report assessing the knowledge of the student based on their ability to answer the teacher's guiding questions. You are to identify which
details within the presentation the student was successful at teaching and which details the student may have answered incorrectly or inadequately at first. 

Here is the conversation history from the presentation which includes the teacher's (model) questions and the student's (user) answers:
{conversation}

Generate a report that comprehensively analyzes what the student answered accurately on their first attempt to articulate the presentation 
and which parts they presented incorrectly or inadequately at first. 
THIS IS IMPORTANT: Use a gentle and supportive but serious tone in your report.

HERE IS AN EXAMPLE OF THE DESIRED FORMAT FOR YOUR RESPONSE (add NOTHING else i.e. do NOT include a title):
'**AREAS OF EXCELLENCE:** 

* **Purpose of Photosynthesis:** After a couple of attempts, the student was able to accurately and concisely state that the purpose of photosynthesis is to convert light to energy.
* **Photosynthetic Organisms:** The student successfully identified algae and plants as photosynthetic organisms. They also correctly identified cyanobacteria when prompted for an additional organism type.
* **Light Source and Energy Function:** The student demonstrated understanding by correctly identifying sunlight as the typical source of light energy and stating that the chemical energy produced fuels the activities of the organisms.

**AREAS FOR IMPROVEMENT:**

* **Initial Definition of Photosynthesis:** While the student could recite a definition of photosynthesis, they struggled to articulate it in their own words. This suggests they may have memorized the definition without fully grasping the concept. Encouraging the student to explain the process in simpler terms could be beneficial. 
* **Delivery and Flow:** While the student provided all the necessary information, it was delivered in a fragmented manner across multiple prompts. This suggests the student might benefit from practicing a more cohesive and natural explanation of the process. 
* **Independent Elaboration:** The student relied heavily on the teacher's cues to provide information. Encouraging the student to elaborate on their initial statements and provide a more complete explanation without prompting would strengthen their understanding and presentation skills. For example, when first asked about the process plants use for energy, the student could have attempted to provide a more self-sufficient definition of photosynthesis before being prompted for specific details.'
""".format(conversation=self.chat.history, lesson=lesson)
        for _ in range(3):
            try:
                llm = GenerativeModel(model_name="gemini-1.5-pro", 
                                      generation_config=self.llm_config, 
                                      safety_settings=self.safety_settings)
                response = llm.generate_content(prompt).text.strip()
                return response
            except Exception as e:
                print("ERROR GENERATING REPORT: {}".format(e))
        print("ERROR GENERATING REPORT.")

class GeminiFlashLLM:

    def __init__(self,
                temperature: float = None,
                top_p: float = None,
                system_instruction: str = None):
        
        credentials_json = {
        "type": "service_account",
        "project_id": keys.VERTEX_AI_PROJECT_ID,
        "private_key_id": keys.VERTEX_AI_PRIVATE_KEY_ID,
        "private_key": keys.VERTEX_AI_PRIVATE_KEY,
        "client_email": keys.VERTEX_AI_CLIENT_EMAIL,
        "client_id": keys.VERTEX_AI_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": keys.VERTEX_AI_CLIENT_X509_CERT_URL,
        "universe_domain": "googleapis.com"
        }
        self.credentials = service_account.Credentials.from_service_account_info(credentials_json)
        self.vertex_ai_location = "us-east1"
        vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)

        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        self.llm_config = GenerationConfig(temperature=temperature, top_p=top_p)
        self.system_instruction = system_instruction
        self.llm = GenerativeModel(model_name="gemini-1.5-flash", 
                                   generation_config=self.llm_config, 
                                   system_instruction=self.system_instruction,
                                   safety_settings=self.safety_settings)

    def switch_vertex_ai_location(self,):
        if self.vertex_ai_location == "us_east1":
            self.vertex_ai_location = "us-central1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)
        elif self.vertex_ai_location == "us-central1":
            self.vertex_ai_location = "us-west1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)
        else:
            self.vertex_ai_location = "us-east1"
            vertexai.init(project=keys.VERTEX_AI_PROJECT_ID, location=self.vertex_ai_location, credentials=self.credentials)

    def generate_content(self,
                         prompt: str,):
        try:
            response = self.llm.generate_content(prompt)
        except Exception as e:
            try:
                self.switch_vertex_ai_location()
                self.llm = GenerativeModel(model_name="gemini-1.5-flash", generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                response = self.llm.generate_content(prompt)
            except Exception as e:
                try:
                    self.switch_vertex_ai_location()
                    self.llm = GenerativeModel(model_name="gemini-1.5-flash", generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    response = self.llm.generate_content(prompt)
                except Exception as e:
                    self.switch_vertex_ai_location()
                    self.llm = GenerativeModel(model_name="gemini-1.5-flash", generation_config=self.llm_config, system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    raise(e)
        # print("[GEMINI 1.5 FLASH]\nINPUT: {} CHARACTERS.\nOUTPUT: {} CHARACTERS.".format(self.llm.count_tokens(prompt).total_billable_characters, self.llm.count_tokens(response.text).total_billable_characters))
        return response

#####################################################################################

def main(topic: str,
         lesson: str,
         student_age: int,
         max_attempts_before_answer_reveal: float = float("inf")):

    main_agent_system_instruction = """You are a teacher teaching {student_age}-year-old students. You have tasked a student of yours with presenting a lesson to the class today. \
This presentation will follow a question+answer format in which you will ask suggestive, guiding questions to the student \
and the student will answer the questions. This back-and-forth will repeat until the student has covered ALL information that is part of the lesson that they are to teach.

The student will teach a lesson discussing the following topic/question: {topic}

Here is the entire lesson that they are to teach about this topic/question by the end of their presentation: {lesson}

You are to repeatedly generate SUGGESTIVE follow up questions that PUSHES them towards teaching the remaining parts of the lesson that they have NOT YET TAUGHT.
IMPORTANTLY, focus on asking questions that emphasize the connections between and understanding of the different concepts in the lesson rather than questions that only require rote memorization!
AVOID ASKING QUESTIONS THAT COVER PARTS OF THE LESSON THAT HAVE ALREADY BEEN COVERED/TAUGHT.
Use a PATIENT but SERIOUS tone that would be used by a supportive teacher teaching {student_age}-year-old students AT ALL TIMES.

THIS IS THE MOST IMPORTANT INSTRUCTION: NEVER ask any question that references or requires knowledge about a topic or detail that is NOT present in the given lesson.

THIS IS CRITICAL: NEVER reveal the answer to ANY previous questions; \
refrain ENTIRELY from implicitly or explicitly SUGGESTING the answer to a previous question even if the student is unable to answer it. \
If a student asks for assistance in the form of you revealing an answer or offering a hint, simply say "I cannot reveal the answer, try thinking harder!" and NOTHING more. \
If a student answers incorrectly, simply say "That isn't quite correct, try thinking harder!" and NOTHING more. \
NEVER EVER answer any questions from the student that may reveal the answer to a previous question; If the student asks a question that may reveal information relevant to a previous question's answer, \
simply say "I cannot answer this question." and NOTHING more.

Once the student is done teaching the lesson i.e. all the information above has been covered, simply say "Looks like we've completed today's lesson!" and NOTHING more.
""".format(student_age=student_age, topic=topic, lesson=lesson)
    
    answer_reveal_system_instruction = """You are a teacher teaching {student_age}-year-old students. You have tasked a student of yours with presenting a lesson to the class today. \
This presentation will follow a question+answer format in which you will ask suggestive, guiding questions to the student \
and the student will answer the questions. This back-and-forth will repeat until the student has covered ALL information that is part of the lesson that they are to teach.

The student will teach a lesson discussing the following topic/question: {topic}

Here is the entire lesson that they are to teach about this topic/question by the end of their presentation: {lesson}

You are to repeatedly generate SUGGESTIVE follow up questions that PUSHES them towards teaching the remaining parts of the lesson that they have not yet taught.
IMPORTANTLY, focus on asking questions that emphasize the connections between and understanding of the different concepts in the lesson rather than questions that only require rote memorization!
AVOID ASKING QUESTIONS THAT COVER PARTS OF THE LESSON THAT HAVE ALREADY BEEN COVERED/TAUGHT.
Use a PATIENT but SERIOUS tone that would be used by a supportive teacher teaching {student_age}-year-old students AT ALL TIMES.

THIS IS THE MOST IMPORTANT INSTRUCTION: NEVER ask any question that references or requires knowledge about a topic or detail that is NOT present in the given lesson.

THIS IS CRITICAL: If a student is confused about the answer to your last question, simply reveal the answer and ask the next \
SUGGESTIVE follow up questions that PUSHES them towards teaching the remaining parts of the lesson that they have not yet taught.

Once the student is done teaching the lesson i.e. all the information above has been covered, simply say "Looks like we've completed today's lesson!" and NOTHING more.
""".format(student_age=student_age, topic=topic, lesson=lesson)
    
    rephrase_questions_as_student_system_instruction = """You are a {student_age}-year-old student. I will give you a question, and you are to REPHRASE it in your own words but NEVER alter its meaning in any way.  \
You are to use language that mimics the nature of how a {student_age}-year-old student would sound. \
However, do NOT use slang or filler words like 'like', maintain professional language and a tone that a {student_age}-year-old student would use in a classroom setting.

THIS IS CRITICAL: Ignore anything in the text I give you that is NOT part of a question. For example, if I give you the phrase "Nice job! Now can you explain why the sky is blue?" you are to \
return "Why is the sky blue?"

IMPORTANT EXCEPTION: If the given question IMPLICITLY OR EXPLICITLY INDICATES that something previously stated was incorrect or needs to be reconsidered/re-thought through, \
simply return "Could you elaborate on that?" and NOTHING more.
""".format(student_age=student_age)
    
    identify_confusion_system_instruction = """I will give you a conversation history between a teacher and student where the teacher (model) will ask questions and the student (user) will respond.

This conversation will pertain to the following information which, IMPORTANTLY, is to be treated as the ground truth: '{lesson}'.

If the student's MOST RECENT response is ENTIRELY incorrect according to the given ground truth information, \
output 'INCORRECT ANSWER DETECTED.' and NOTHING more. \
HOWEVER, if the student's most recent response is correct even PARTIALLY, output 'NO INACCURACY DETECTED.' and NOTHING more.
""".format(lesson=lesson)
    
    llm_agent = GeminiLLM(temperature=0.2, 
                          top_p=0.1, 
                          system_instruction=main_agent_system_instruction)
    
    answer_reveal_agent = GeminiLLM(temperature=0.2, 
                                    top_p=0.1, 
                                    system_instruction=answer_reveal_system_instruction)
    
    confusion_detection_agent = GeminiFlashLLM(temperature=0.2,
                                               top_p=0.1,
                                               system_instruction=identify_confusion_system_instruction)
    
    rephrase_questions_agent = GeminiFlashLLM(temperature=0.2,
                                              top_p=0.1,
                                              system_instruction=rephrase_questions_as_student_system_instruction)
    
    student_answer, first_question = "Hello! I'm ready to begin teaching today's lesson about the following: {}.".format(topic), True
    confusion_detected, consecutive_confusions = False, 0
    while True:
        next_question = llm_agent.send_message(student_answer).text.strip()
        if "Looks like we've completed today's lesson!" in next_question:
            print("TEACHER: {}".format(next_question))
            break
        if confusion_detected:
            consecutive_confusions += 1
            print("INACCURACY #{} DETECTED!".format(consecutive_confusions))
            print("-"*150)
            if consecutive_confusions >= max_attempts_before_answer_reveal:
                answer_reveal_agent.set_history(llm_agent.get_history()[:-2])
                next_question = answer_reveal_agent.send_message(student_answer).text.strip()
                llm_agent.set_history(answer_reveal_agent.get_history())
                consecutive_confusions = 0
            print("TEACHER: {}".format(next_question))
            if "Looks like we've completed today's lesson!" in next_question:
                break
        else:
            consecutive_confusions = 0
            if first_question:
                print("TEACHER: {}".format(next_question))
                first_question = False
            else:
                next_question = rephrase_questions_agent.generate_content(next_question).text.strip()
                print("OTHER STUDENT: {}".format(next_question))
        print("-"*150)
        student_answer = input("YOUR ANSWER: ")
        chat_history_as_string = ""
        for element in llm_agent.get_history():
            if element.role == "model":
                chat_history_as_string += "TEACHER: '{}'\n".format(element.parts[0].text.strip())
            elif element.role == "user":
                chat_history_as_string += "STUDENT: '{}'\n".format(element.parts[0].text.strip())
        chat_history_as_string += "STUDENT'S MOST RECENT ANSWER: '{}'".format(student_answer)
        confusion_detected = "NO INACCURACY DETECTED" not in confusion_detection_agent.generate_content(chat_history_as_string).text
        print("-"*150)
    final_report = llm_agent.generate_final_report(lesson=lesson)
    print(final_report)
    print("-"*150)

if __name__ == "__main__":

    student_age = 10

    question = """QUESTION: Former astronaut Ellen Ochoa says that although she
doesn’t have a definite idea of when it might happen,
she _______ that humans will someday need to be
able to live in other environments than those found
on Earth. This conjecture informs her interest in
future research missions to the moon.

Which choice completes the text with the most
logical and precise word or phrase?

Which choice completes the text with the most
logical and precise word or phrase?
A. demands
B. speculates
C. doubts
D. establishes"""

    answer = """ANSWER: B. speculates

EXPLANATION: Choice B is the best answer because it most logically completes the text’s
discussion of Ochoa’s prediction that humans will one day need to live in places
other than Earth. As used in this context, “speculates” would mean puts forward
an idea without firm evidence. The text states that Ochoa “doesn’t have a
definite idea” about when humans might need to live in other environments and
characterizes Ochoa’s prediction as a “conjecture,” or a conclusion presented
without convincing evidence. This context indicates that Ochoa speculates when
she makes this prediction.
Choice A is incorrect because saying that Ochoa “demands,” or insists or
requires, that humans will one day need to live in other environments than Earth’s
wouldn’t make sense in context. The text indicates that she’s unsure about
the timing but hypothesizes that it will someday happen. Choice C is incorrect
because saying that Ochoa “doubts,” or questions or disbelieves, that humans
will one day need to live in other environments than Earth’s wouldn’t make sense
in context. The text indicates that although Ochoa is unsure about the timing,
she hypothesizes that humans will need to live in places other than Earth and
encourages research into future travel to the moon. Choice D is incorrect because
saying that Ochoa “establishes,” or proves, that humans will one day need to
live in other environments than Earth’s wouldn’t make sense in context. Rather
than stating that Ochoa discusses her idea with certainty and supports it with
evidence, the text indicates that Ochoa is unsure about when humans might need
to live in other environments."""

    main(topic=question, lesson=answer, student_age=student_age, max_attempts_before_answer_reveal=2)