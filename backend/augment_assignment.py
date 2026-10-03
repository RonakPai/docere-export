'''
All AI augmenting of assignments.
'''

import re

from llm_classes import GeminiLLM, GeminiFlashLLM
import rds_management
import quota_management

def generate_final_report_helper(assignment_id: str,
                                 student_username: str,
                                 student_attempt: int) -> str:
    
    assignment_info = rds_management.get_assignment_info(assignment_id=assignment_id)
    progress = rds_management.get_progress(assignment_id=assignment_id, student_username=student_username, student_attempt=student_attempt)

    topic = "**TOPIC:**\n{}\n\n**QUESTION(S):**\n{}".format(assignment_info['topic'], assignment_info['question'])

    final_report = generate_final_report(history_as_string=progress['history_as_string'],
                                         topic=topic,
                                         lesson=progress['ai_augmented_lesson'])
    _ = rds_management.insert_final_report(assignment_id=assignment_id,
                                           student_username=student_username,
                                           student_attempt=student_attempt,
                                           final_report=final_report)
    
    return final_report

def generate_final_report(history_as_string: str,
                          topic: str,
                          lesson: str) -> str:
    prompt = """\
You are observing a lesson being presented by a student;
This presentation will follow a question+answer format in which the teacher will ask suggestive, guiding questions to the student \
and the student will answer the teacher's questions. This back-and-forth will repeat until the student has covered ALL information that is part of the lesson that they are to teach.

The presentation will discuss the following topic/question: '{topic}'.

This presentation will pertain to the following information which, IMPORTANTLY, is to be treated as the GROUND TRUTH in regards to the above topic/question: '{lesson}'.

Your task is to draft an EXTENSIVE report assessing the knowledge of the student based on their ability to deliver the lesson content. You are to identify which \
details within the lesson the student was successful at teaching and which details the student may have covered incorrectly, incompletely, or inadequately at first. \
EVALUATE the lesson the lens of an other student listening to the lesson and learning the presented information for the first time - identify which elements of the lesson were taught well and what could have been taught better. \
Here are some key things to look for:\
1. Continuity/Logical Flow is important. The lesson should not be presented as a set of independent facts, the student should deliver the lesson in a way that LOGICALLY flows.
2. Crystallization of complex concepts. The student should place extra emphasis in their lesson on topics that may be difficult to understand for a learner learning it all for the first time, \
through repeating the concept multiple times, simplifying the concept, correcting common misconceptions about the concept, and/or real world examples/connections.
Each bullet point in your report should make an explicit reference to direct quote(s) from the student from the given conversation.

THIS IS EXTREMELY IMPORTANT: The student is NOT expected to discuss or know ANY INFORMATION OUTSIDE OF THE GROUND TRUTH INFORMATION GIVEN ABOVE. Their knowledge of additional or tangential information
should NOT be considered when you draft your report.

Here is the conversation history from the presentation which includes the teacher's (model) questions and the student's (user) answers:
{conversation}

Generate a report that comprehensively analyzes what the student answered accurately on their first attempt to articulate the presentation 
and which parts they presented incorrectly or inadequately at first. 
THIS IS IMPORTANT: Use a gentle but serious tone in your report.

HERE IS AN EXAMPLE OF THE DESIRED FORMAT FOR YOUR RESPONSE (add NOTHING else i.e. do NOT include a title):
'**AREAS OF EXCELLENCE:**

* **Overview of Factors Leading to WWI:** The student effectively introduced the concept that World War I was caused by a complex interplay of factors rather than a single event. They identified three key areas: motives of key players, pre-war events, and interactions leading to escalation. ("Okay, so to understand the outbreak of World War I, we need to look at it as a sort of perfect storm of different factors.  It wasn't just one thing, but a bunch of things all coming together.  We can break this down into three main parts: the motives of the key players, the events leading up to the war, and the web of interactions that tied everything together.")
* **Motivations of Major Powers:** The student accurately described the primary motivations and anxieties of Germany, Austria-Hungary, Russia, Great Britain, and France in the years leading up to World War I. ("Sure.  So, each of these major powers had their own ambitions and anxieties that kind of bumped up against each other... Basically, everyone wanted to be on top or were afraid of someone else getting too strong.  This made for a very unstable situation where even small disputes could blow up into something much bigger.")
* **Britain's Concerns about Germany:** The student correctly identified Britain's fear of Germany's growing naval power as a threat to their global dominance and trade. ("Britain was mainly worried about Germany threatening its status as the top global naval power.  They saw Germany building a bigger navy and thought it challenged their control of the seas, which was vital for their empire and trade.")
* **France's Resentment towards Germany:** The student accurately explained France's desire to regain its status after the Franco-Prussian War and their perception of Germany's growing power as a threat. ("France was defeated by Germany in the Franco-Prussian War, which took place from 1870 to 1871. This loss was a significant blow to French national pride and led to a deep resentment towards Germany. In the years leading up to World War I, France was eager to regain its status as a major European power and saw Germany's growing power as a direct threat.")
* **Russia's Role as Protector of Slavs:** The student provided a clear and concise explanation of Russia's self-proclaimed role as protector of Slavic people, particularly in the Balkans, and how this contributed to tensions with Austria-Hungary. ("The Slavs are an ethnolinguistic group of people in Europe who share common ancestry and, often, similar languages and cultural traditions... Russia felt like it needed to stand up for these Slavic groups against other empires, and this is one reason why the Balkans were such a point of conflict between Russia and Austria-Hungary.")
* **The Great Game:** The student accurately described the Great Game as a rivalry between Britain and Russia for influence in Central Asia and how it contributed to overall tension in Europe. ("The \"Great Game\" was a rivalry between Britain and Russia for control and influence in Central Asia... This constant struggle for dominance created a lot of suspicion and tension between the two countries, which spilled over into their relationships with other European powers and contributed to the overall instability that led to the war.")
* **Britain's Motivation in the Moroccan Crisis:** The student correctly explained Britain's intervention in the Moroccan Crisis as an attempt to maintain the balance of power in Europe and prevent Germany from becoming too dominant. ("Not quite! While it's true that Britain and Germany were rivals, a war between France and Germany wouldn't have been in Britain's best interest.  See, a key part of Britain's foreign policy was maintaining the balance of power in Europe... If Germany defeated France, they would become too powerful, upsetting that balance and threatening Britain's own interests.")
* **Alliance Systems and the Risk of War:** The student effectively explained the role of alliance systems (Triple Entente and Triple Alliance) in increasing the likelihood of a large-scale war by obligating countries to defend their allies. ("Yeah, so basically, the big powers in Europe had formed these two main alliances... The problem was that these alliances meant that if one country got into a fight, it could drag all its allies into the conflict too... This system meant that a small conflict could quickly spiral into a huge one, drawing in more and more countries because of their alliances.")
* **The Arms Race and Fear:** The student accurately described the arms race as a cycle of fear and mistrust, where each country's military buildup fueled the anxieties of others, leading to a highly unstable situation. ("The arms race was basically a vicious cycle fueled by fear and mistrust between the major powers... It created a really dangerous situation where everyone was on edge and a small incident could easily spiral out of control.")
* **Nationalism and Militarism:** The student provided clear definitions of nationalism and militarism and accurately explained how these ideologies contributed to the likelihood of war. ("Nationalism was a powerful force back then... Militarism goes hand in hand with this: it's the belief that a strong military is essential and that military solutions are the best way to solve problems. So, you have all these proud nations with big armies, making them more likely to jump into war.")
* **Assassination of Archduke Franz Ferdinand:** The student correctly identified the assassination of Archduke Franz Ferdinand as the immediate trigger for World War I. ("The assassination of Archduke Franz Ferdinand. He was the heir to the Austro-Hungarian throne, and he was assassinated by a Serbian nationalist in Sarajevo in 1914. This event was the immediate trigger that set off the chain reaction of alliances and declarations of war that started World War I.")
* **Assassination as Trigger, Not Sole Cause:** The student accurately emphasized that the assassination was a trigger, not the sole cause of the war, highlighting the pre-existing tensions and alliances that turned a single event into a global conflict. ("The assassination of Archduke Franz Ferdinand was the trigger, not the cause of the war... Austria-Hungary saw the assassination, which was linked to Serbia, as an opportunity to assert dominance in the Balkans... So, one event spiraled into a global conflict because of these pre-existing tensions and alliances.")

**AREAS FOR IMPROVEMENT:**

* **Specificity in the Great Game:** While the student accurately described the Great Game, they could improve by providing more specific examples of the actions taken by Britain and Russia in their rivalry. ("The \"moves\" in the Great Game weren't as defined as a chess match, but more like a constant back-and-forth of political maneuvering and military posturing... It was a constant struggle for dominance in Central Asia, with both sides trying to outmaneuver the other.") Providing concrete examples, such as British alliances in Afghanistan or Russian influence in Persia, would create a more engaging and informative explanation.
* **Connecting the Balkan Wars to the Larger Conflict:** The student initially struggled to explain how the Balkan Wars, a seemingly distant conflict, increased the likelihood of a wider European war. ("The Balkan Wars happened in 1912 and 1913... This really messed things up in the Balkans and made the rivalry between the big European powers even worse, pushing them closer to war."  and "I don't know.") While they eventually provided a more complete answer, this highlights an area where they could benefit from a deeper understanding of the interconnectedness of events and the ripple effect of regional conflicts.
* **Expanding on the Arms Race:** While the student correctly identified the arms race as a key factor, their initial explanation was simplistic and lacked depth. ("An arms race is when countries compete to build bigger armies.  It caused the war by making the countries have really big armies.") They could improve by elaborating on the fear and suspicion that fueled the arms race, providing specific examples like the naval rivalry between Britain and Germany.
* **Illustrating Nationalism with Examples:** The student accurately defined nationalism but could strengthen their explanation by providing concrete examples of how this ideology manifested in the years before World War I. ("Absolutely!  A big part of nationalism is this idea that your country is superior to others... This constant arms race created a climate of fear and suspicion, where even the slightest provocation could be interpreted as a threat.") They could discuss specific instances of nationalistic rhetoric, territorial disputes, or cultural clashes that heightened tensions between nations.
* **Overall Flow and Cohesiveness:** While the student provided accurate information, their responses sometimes felt fragmented and disconnected. This suggests that they might benefit from practicing a more cohesive and naturally flowing explanation of the events leading to World War I. Encouraging the student to connect the different factors and events in a more narrative-driven approach would make the lesson more engaging and easier to follow.'
If there is nothing to list in either section, simply list "* **NONE**" in that section.
""".format(conversation=history_as_string, topic=topic, lesson=lesson)
    for _ in range(3):
        try:
            final_report_generation_agent = GeminiLLM(0.2, 0.1)
            return final_report_generation_agent.generate_content(prompt).text.strip()
        except Exception as e:
            print("ERROR GENERATING REPORT: {}".format(e))
    print("ERROR GENERATING REPORT.")

def get_assignment_report(assignment_id: str,
                          student_username: str,
                          student_attempt: int,):
    
    def process_assignment_report(report: str,):
        strengths_section = report[re.search(r'\*\*AREAS OF EXCELLENCE:\*\*', report).end():re.search(r'\*\*AREAS FOR IMPROVEMENT:\*\*', report).start()]
        strengths = [element.strip() for element in strengths_section.split("\n* ") if (len(element.strip()) > 0 and '**NONE**' not in element)]
        weaknesses_section = report[re.search(r'\*\*AREAS FOR IMPROVEMENT:\*\*', report).end():]
        weaknesses = [element.strip() for element in weaknesses_section.split("\n* ") if (len(element.strip()) > 0 and '**NONE**' not in element)]
        return {'Strengths': strengths,
                'Weaknesses': weaknesses}
    
    final_report = rds_management.get_final_report(assignment_id=assignment_id,
                                             student_username=student_username,
                                             student_attempt=student_attempt)['final_report']
    if final_report == "":
        final_report = generate_final_report_helper(assignment_id=assignment_id,
                                                    student_username=student_username,
                                                    student_attempt=student_attempt)
    return process_assignment_report(report=final_report)

def augment_lesson(topic: str,
                   question: str,
                   lesson: str,
                   lesson_length: int = 30,
                   student_age: int = 21,
                   strengths: list[str] = [],
                   weaknesses: list[str] = [],):
    
    original_lesson_word_count = len(lesson.split())
    lesson_word_count_lower_bound = min(original_lesson_word_count*2, lesson_length*75)
    lesson_word_count_upper_bound =  min(lesson_word_count_lower_bound*2, lesson_word_count_lower_bound+50)
    
    system_instruction = """I will give you information from a lesson plan that is to be delivered to a student learning the information for the first time; \
you are to revise and rewrite this lesson to emphasize, reiterate, and clarify \
the parts of the information that could be confusing to a student learning the material for the first time.
I will provide you with helpful context on the topic and question(s) being discussed in the lesson; 
HOWEVER, you are to ONLY revise the lesson plan, do NOT touch the topic or question(s) in any way.

Leverage the following techniques to revise the lesson:
1. Repetition of concepts, perhaps from multiple angles/perspectives.
2. THIS TECHNIQUE IS CRITICAL, DO THIS WHEREVER POSSIBLE: Explicit, preemptive identification and correction of common misconceptions related to the concepts.
3. THIS TECHNIQUE IS VERY POWERFUL, DO THIS AS OFTEN AS POSSIBLE: Preemtively address logical counterarguments, counterpoints, and alternate ideas (derived from common knowledge/logic) that challenge ideas or concepts in the lesson.

Make the lesson as long, detailed, and revision-dense as possible while satisfying the following constraints.
1. Use a serious tone and style when rewriting the lesson plan.
2. Your revised lesson plan should be between {lesson_word_count_lower_bound} and {lesson_word_count_upper_bound} words long. Do NOT exceed this word count range. 
3. Do NOT omit any information from the original lesson in your revised lesson. 
4. THIS IS THE MOST IMPORTANT CONSTRAINT: Do not ADD any information to the original lesson that is outside of the scope of common knowledge, \
that is, do not add TECHNICAL knowledge to the lesson, simply crystallize the lesson further using common knowledge.
5. Format the revised lesson as a set of bullet points (can use sub-bullet points as well). However, beyond using the '*' symbol as a bullet point, \
do NOT use any sort of markdown formatting (i.e. do not bold words/phrases); only use whitespace or punctuation for formatting.
""".format(lesson_word_count_lower_bound=lesson_word_count_lower_bound,
           lesson_word_count_upper_bound=lesson_word_count_upper_bound)

    if len(weaknesses) > 0:
        system_instruction += "\n\nIn addition to the other complex/confusing concepts of the lesson, be sure to place EXTRA emphasis on the following elements of the lesson in your revised version:"
        for element in weaknesses:
            system_instruction += "\n* {}".format(element)

    if len(strengths) > 0:
        system_instruction += "\n\nPlace LESS emphasis on the following elements of the lesson in your revised version:"
        for element in strengths:
            system_instruction += "\n* {}".format(element)

    for _ in range(3):
        try:
            lesson_revision_agent = GeminiLLM(temperature=0.2,
                                              top_p=0.1,
                                              system_instruction=system_instruction,)
            prompt = """\
HERE IS THE LESSON PLAN ({original_lesson_word_count} WORDS LONG):
'{lesson}'""".format(original_lesson_word_count=original_lesson_word_count, lesson=lesson)
            revised_lesson = lesson_revision_agent.generate_content(prompt).text.strip()
            return revised_lesson
        except Exception as e:
            print("ERROR REVISING LESSON: {}".format(e))
    print("ERROR REVISING LESSON.")

def augment_lesson_on_lesson_join(topic: str,
                                  question: str,
                                  lesson: str,
                                  lesson_length: int = 30,
                                  student_age: int = 21,
                                  strengths: list[str] = [],
                                  weaknesses: list[str] = [],):
    
    original_lesson_word_count = len(lesson.split())
    lesson_word_count_lower_bound = original_lesson_word_count
    lesson_word_count_upper_bound =  min(lesson_word_count_lower_bound*2, lesson_word_count_lower_bound+50)
    
    system_instruction = """I will give you information from a lesson plan that is to be delivered to a student learning the information for the first time; \
you are to revise (only where needed) this lesson to emphasize, reiterate, and clarify \
only the parts of the information that are not yet emphasized/stressed that could be confusing to a student learning the material for the first time.
I will provide you with helpful context on the topic and question(s) being discussed in the lesson; 
HOWEVER, you are to ONLY revise the lesson plan, do NOT touch the topic or question(s) in any way.

Leverage the following two techniques to revise the lesson ONLY WHERE THESE TECHNIQUES HAVE NOT ALREADY BEEN USED:
1. THIS TECHNIQUE IS CRITICAL, DO THIS WHEREVER POSSIBLE: Explicit, preemptive identification and correction of common misconceptions related to the concepts.
2. THIS TECHNIQUE IS VERY POWERFUL, DO THIS AS OFTEN AS POSSIBLE: Preemtively address logical counterarguments, counterpoints, and alternate ideas (derived from common knowledge/logic) that challenge ideas or concepts in the lesson.

Make sure to satisfy the following constraints.
1. Use a serious tone and style when revising the lesson plan.
2. Do NOT alter the lesson length. Your revised lesson plan should be between {lesson_word_count_lower_bound} and {lesson_word_count_upper_bound} words long. Do NOT exceed this word count range. 
3. Do NOT omit any information from the original lesson in your revised lesson. 
4. THIS IS THE MOST IMPORTANT CONSTRAINT: Do not ADD any information to the original lesson that is outside of the scope of common knowledge, \
that is, do not add TECHNICAL knowledge to the lesson, simply crystallize the lesson further using common knowledge.
5. Format the revised lesson as a set of bullet points (can use sub-bullet points as well). However, beyond using the '*' symbol as a bullet point, \
do NOT use any sort of markdown formatting (i.e. do not bold words/phrases); only use whitespace or punctuation for formatting.
""".format(lesson_word_count_lower_bound=lesson_word_count_lower_bound,
           lesson_word_count_upper_bound=lesson_word_count_upper_bound)

    if len(weaknesses) > 0:
        system_instruction += "\n\nNow, this is the MOST IMPORTANT TASK OF YOUR REVISION: REVISE THE LESSON TO place EXTRA emphasis on the following elements as these elements NEED to be further emphasized:"
        for element in weaknesses:
            system_instruction += "\n* {}".format(element)

    if len(strengths) > 0:
        system_instruction += "\n\nAlso, place LESS emphasis on the following elements of the lesson in your revised version:"
        for element in strengths:
            system_instruction += "\n* {}".format(element)

    for _ in range(3):
        try:
            lesson_revision_agent = GeminiLLM(temperature=0.2,
                                              top_p=0.1,
                                              system_instruction=system_instruction,)
            prompt = """\
HERE IS THE TOPIC BEING DISCUSSED IN THE LESSON:
'{topic}'

HERE IS THE ASSOCIATED QUESTION(S) BEING DISCUSSED IN THE LESSON:
'{question}'

HERE IS THE LESSON PLAN ({original_lesson_word_count} WORDS LONG):
'{lesson}'""".format(topic=topic, question=question, original_lesson_word_count=original_lesson_word_count, lesson=lesson)
            revised_lesson = lesson_revision_agent.generate_content(prompt).text.strip()
            return revised_lesson
        except Exception as e:
            print("ERROR REVISING LESSON: {}".format(e))
    print("ERROR REVISING LESSON.")

def regenerate_lesson(assignment_id: str,
                      student_username: str,
                      student_attempt: int,
                      lesson_length: int,):
    
    new_student_attempt = rds_management.get_num_attempts(assignment_id=assignment_id, student_username=student_username) + 1
    max_attempts = quota_management.get_num_attempts_per_assignment_quota(student_username=student_username)
    if max_attempts < new_student_attempt:
        return {"status": "Error.",
                "message": "User '{}' can only regenerate assignments up to {} time(s).".format(student_username, max_attempts-1)}
    
    assignment_report = get_assignment_report(assignment_id=assignment_id, 
                                              student_username=student_username, 
                                              student_attempt=student_attempt)
    assignment_info = rds_management.get_assignment_info(assignment_id=assignment_id)
    
    new_lesson = augment_lesson(topic=assignment_info['topic'],
                                question=assignment_info['question'],
                                lesson=assignment_info['lesson'],
                                lesson_length=lesson_length,
                                student_age=assignment_info['student_age'],
                                strengths=assignment_report['Strengths'],
                                weaknesses=assignment_report['Weaknesses'])
    _ = rds_management.update_progress(assignment_id=assignment_id,
                                       student_username=student_username,
                                       student_attempt=new_student_attempt,
                                       ai_augmented_lesson=new_lesson)
    
    return {'assignment_id': assignment_id,
            'student_username': student_username,
            'student_attempt': new_student_attempt}

def generate_first_prompt(topic: str = "",
                          lesson: str = "",):
     
    generate_first_prompt_system_instruction = """I will give you a topic and a presentation pertaining to the topic.
come up with a prompt DIRECTED TO THE PRESENTER to kick off their presentation. \
This prompt should be in the form of a formal question that can be answered. \
Ensure that this question guides the presenter to begin their presentation at a logical starting point that enables their presentation to flow smoothly and logically \
from start to finish.

Simply return the prompt and nothing else."""

    prompt = """HERE IS THE TOPIC: 
{topic}

HERE IS THE PRESENTATION:
{lesson}""".format(topic=topic, lesson=lesson)
    
    generate_first_prompt_agent = GeminiFlashLLM(temperature=0.2,
                                                 top_p=0.1,
                                                 system_instruction=generate_first_prompt_system_instruction)
    return generate_first_prompt_agent.generate_content(prompt=prompt).text.strip()

def generate_assignment_contents(lesson_contents: str = "",):
    
    
    def generate_title(lesson_contents: str = "",):
        
        system_instruction = """\
I am a professor. I will give you the contents of a lesson I am going to deliver to my students; Come up with ONE concise, professional title for the lesson.
Output nothing but the title itself.
Example Output: "The Nitrogen Cycle"
"""
    
        agent = GeminiFlashLLM(temperature=0.2,
                               top_p=0.1,
                               system_instruction=system_instruction)
        return agent.generate_content(prompt=lesson_contents).text.strip()
    
    def generate_task_description(lesson_contents: str = "",):
        
        system_instruction = """\
I will give you the contents of a lesson I am going to deliver. Come up with a one sentence description \
of the TOPIC that I will be discussing in this lesson. Your one sentence description should begin with "Discuss..."
Output nothing but the description.
Example Output: "Discuss the nitrogen cycle."
"""
    
        agent = GeminiFlashLLM(temperature=0.2,
                               top_p=0.1,
                               system_instruction=system_instruction)
        return agent.generate_content(prompt=lesson_contents).text.strip()
    
    output = {"title": "",
              "task_description": "",
              "first_prompt": ""}
    
    output['title'] = generate_title(lesson_contents=lesson_contents)
    output['task_description'] = generate_task_description(lesson_contents=lesson_contents)
    output['first_prompt'] = generate_first_prompt(topic=output['task_description'],
                                                   lesson=lesson_contents)
    
    return output
    
