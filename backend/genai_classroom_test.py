import json
import random

import app

def run_tests(env: str = "local"):

    valid_envs = ['local', 'production'] # (1) 'local' calls local backend APIs (2) 'production' calls deployed backend APIs
    if env not in valid_envs:
        print("INVALID ENVIRONMENT SELECTION, PICK FROM THE FOLLOWING: {}".format(valid_envs))
    print("-"*150)

    student_age = 22
    max_attempts_before_answer_reveal=2

    assignment_title = "World War 1"
    subject = "AP US History"

    topic = """World War 1"""

    questions = """Discuss the motives/mindsets of the actors involved, the series of preceding events, and the massive network of \
interactions between these actors and events that snowballed and culminated in the start of World War I."""

    first_prompt = """Let's discuss the motives/mindsets of the actors involved, the series of preceding events, and the massive network of \
interactions between these actors and events that snowballed and culminated in the start of World War I."""

    lesson = """
The Road to World War I: A Complex Tapestry
The outbreak of World War I was a cataclysmic event that reshaped the global political landscape. It was not a singular incident but a culmination of a series of interconnected factors, each contributing to the escalating tensions that ultimately led to war.

Motives and Mindsets of the Key Actors
Germany: The German Empire, under the leadership of Kaiser Wilhelm II, sought to establish itself as a dominant power in Europe. Its rapid industrialization and military buildup created a sense of national pride and ambition. Germany's expansionist policies, particularly in the Balkans and Africa, were seen as a threat by other European powers.
Austria-Hungary: The Austro-Hungarian Empire was facing internal challenges, including the growing discontent of its ethnic minorities. The empire sought to maintain its territorial integrity and dominance in the Balkans, which was a region of intense rivalry among European powers.
Russia: Russia, as a major European power, had a longstanding interest in the Balkans and sought to protect the interests of Slavic populations in the region. Its rivalry with Austria-Hungary over the Balkans was a key factor in the escalating tensions.
Britain: Britain, as the dominant naval power, sought to maintain its global empire and influence. It was concerned about the growing power of Germany and its potential threat to British interests.
France: France, which had been defeated by Germany in the Franco-Prussian War, sought to regain its status as a major European power. It was also concerned about German expansionist ambitions and sought to form alliances to counter German influence.
Preceding Events and Interactions
The Great Game: The rivalry between Britain and Russia for influence in Central Asia, known as the Great Game, created a tense atmosphere and contributed to the broader European power struggle.
The Moroccan Crisis: In 1905, Germany challenged France's control over Morocco, leading to a diplomatic crisis that was resolved with British mediation. However, the incident demonstrated the growing tensions between Germany and the Entente powers (Britain, France, and Russia).
The Balkan Wars: The Balkan Wars of 1912-1913 saw the Balkan states unite to expel the Ottoman Empire from the region. These wars further destabilized the Balkans and intensified the rivalry between the major European powers.
The Network of Interactions and Escalation
Alliance Systems: The formation of the Triple Entente (Britain, France, and Russia) and the Triple Alliance (Germany, Austria-Hungary, and Italy) created two competing blocs that significantly increased the likelihood of a major war.
Arms Race: The growing competition between the European powers led to a massive arms race, as nations sought to build up their military capabilities to deter potential aggression.
Nationalism and Militarism: The rise of nationalism and militarism in many European countries fueled aggressive foreign policies and made it more difficult to resolve disputes peacefully.
The Assassination of Archduke Franz Ferdinand: The assassination of Archduke Franz Ferdinand, heir to the Austro-Hungarian throne, by a Serbian nationalist in Sarajevo in 1914 provided the immediate spark that ignited the Great War.   
The complex interplay of these factors, combined with the existing tensions and rivalries between European powers, created a volatile environment that ultimately led to the outbreak of World War I. The war had a devastating impact on Europe and the world, leaving a lasting legacy that continues to shape global politics today."""

    assignment_creator_username = "adhit@docerelearning.com"
    assignment_creator_name = "Adhit Sankaran"
    assignment_creator_organization = "Docere Learning"

    student_username = "adhit@docerelearning.com"
    student_name = "Adhit Sankaran"
    student_organization = "Docere Learning"

    student_attempt = 1

    # onboard TEACHER
    payload = {
        "username": assignment_creator_username,
        "name": assignment_creator_name,
        "organization": assignment_creator_organization,
        "subscription_tier": "school",
    }
    if env == "local":
        response = app.app.test_client().post('/onboard_user/', json=payload).text
        print(response)
    else: # env == "production"
        pass
    print("-"*150)

    # onboard STUDENT
    payload = {
        "username": student_username,
        "name": student_name,
        "organization": student_organization,
        "subscription_tier": "school",
    }
    if env == "local":
        response = app.app.test_client().post('/onboard_user/', json=payload).text
        print(response)
    else: # env == "production"
        pass
    print("-"*150)

    # create assignment
    payload = {
        "creator_username": assignment_creator_username,
        "assignment_title": assignment_title,
        "subject": subject,
        "first_prompt": first_prompt,
        "topic": topic,
        "question": questions,
        "lesson": lesson,
        "lesson_length": 40,
        "student_age": student_age,
        "max_attempts_before_answer_reveal":max_attempts_before_answer_reveal
    }
    response = json.loads(app.app.test_client().post('/create_assignment/', json=payload).text)
    assignment_id = response['assignment_id']
    print("'{}' CREATED ASSIGNMENT '{}'.".format(assignment_creator_username, assignment_id))
    print("-"*150)

    # add student to assignment
    payload = {
        "assignment_id": assignment_id,
        "student_username": student_username,
    }
    response = json.loads(app.app.test_client().post('/join_assignment/', json=payload).text)
    try:
        assignment_id = response['assignment_id']
        student_username = response['student_username']
        print("ADDED '{}' TO ASSIGNMENT '{}'.".format(student_username, assignment_id))
        print("-"*150)
    except:
        print(response['message'])

    # check student's in-progress assignments
    payload = {
        "student_username": student_username,
    }
    response = json.loads(app.app.test_client().post('/get_in_progress_assignments/', json=payload).text)
    print("IN-PROGRESS ASSIGNMENTS FOR USER '{}': {}".format(student_username, response))
    print("-"*150)

    # assignment
    payload = {
        "assignment_id": assignment_id,
    }
    first_prompt = json.loads(app.app.test_client().post('/get_assignment_info/', json=payload).text)['first_prompt']
    print('AI-TEACHING ASSISTANT: {}'.format(first_prompt))
    print("-"*150)
    next_question = first_prompt
    while True:
        # student_answer = input("YOU: ")
        correct_answer_prob = 0.6
        print("YOU: ", end="")
        correct_payload = {
            "assignment_id": assignment_id,
            "username": assignment_creator_username,
            "next_question": next_question,
            "correct": True
        }
        incorrect_payload = {
            "assignment_id": assignment_id,
            "username": assignment_creator_username,
            "next_question": next_question,
            "correct": False
        }
        if env == "local":
            if random.random() < correct_answer_prob: # generate correct answer
                student_answer = app.app.test_client().post('/get_ai_presenter_answer/', json=correct_payload).text
            else: # generate incorrect answer
                student_answer = random.choice(['I don\'t know.', 'GENERATE INCORRECT ANSWER', 'GENERATE INCORRECT ANSWER'])
                if student_answer == "GENERATE INCORRECT ANSWER":
                    student_answer = app.app.test_client().post('/get_ai_presenter_answer/', json=incorrect_payload).text
        else: # env == "production"
            pass
        
        print(student_answer)
        print("-"*150)
        payload = {
            "student_answer": student_answer,
            "assignment_id": assignment_id,
            "student_username": student_username,
            "student_attempt": student_attempt
        }
        if env == "local":
            response = json.loads(app.app.test_client().post('/get_next_question/', json=payload).text)
        else: # env == "production"
            pass
        actor, next_question, lesson_completed, progress_bar = response['actor'], response['next_question'], response['lesson_completed'], response['progress_bar']
        print("{}% OF LESSON COMPLETED!".format(progress_bar))
        print("-"*150)
        actor = "AI-TEACHING ASSISTANT" if actor == "TEACHER" else actor
        actor = "AI-STUDENT" if actor == "STUDENT" else actor
        print("{}: {}".format(actor, next_question))
        print("-"*150)
        if lesson_completed:
            payload = {
                "assignment_id": assignment_id,
                "student_username": student_username,
                "student_attempt": student_attempt
            }
            if env == "local":
                response = json.loads(app.app.test_client().post('/get_assignment_progress/', json=payload).text)
            else: # env == "production"
                pass
            print("TIME ELAPSED: {} SECONDS.".format(response['end_time']-response['start_time']))
            print("-"*150)
            break
    
    # generate report on assignment
    payload = {
        "assignment_id": assignment_id,
        "student_username": student_username,
        "student_attempt": student_attempt
    }
    if env == "local":
        response = json.loads(app.app.test_client().post('/generate_assignment_report/', json=payload).text)
    else: # env == "production"
        pass
    print("FINAL REPORT: {}".format(response))
    print("-"*150)

    for i in range(6):

        break # uncomment to test assignment regeneration

        # regenerate assignment based on report
        payload = {
            "assignment_id": assignment_id,
            "student_username": student_username,
            "student_attempt": student_attempt,
            "lesson_length": 5
        }
        if env == "local":
            response = app.app.test_client().post('/regenerate_assignment/', json=payload).text
        else: # env == "production"
            pass
        print("REGENERATED ASSIGNMENT API INPUTS: {}".format(json.loads(response)))
        print("-"*150)

        # check for regenerated assignment progress info
        payload = {
            "assignment_id": assignment_id,
            "student_username": student_username,
            "student_attempt": student_attempt+i+1
        }
        if env == "local":
            response = app.app.test_client().post('/get_assignment_progress/', json=payload).text
        else: # env == "production"
            pass
        print("REGENERATED ASSIGNMENT RETRIEVED INFO: {}".format(json.loads(response)))
        print("-"*150)

    # list public assignments
    payload = {
        "subject": subject
    }
    if env == "local":
        response = json.loads(app.app.test_client().post('/get_all_public_assignments/', json=payload).text)
        print("PUBLIC {} ASSIGNMENTS: {}".format(subject, response))
    else: # env == "production"
        pass
    print("-"*150)

    # # offboard TEACHER
    # payload = {
    #     "username": assignment_creator_username
    # }
    # if env == "local":
    #     response = app.app.test_client().post('/offboard_user/', json=payload).text
    # else: # env == "production"
    #     pass
    # print("-"*150)

    # # offboard STUDENT
    # payload = {
    #     "username": student_username
    # }
    # if env == "local":
    #     response = app.app.test_client().post('/offboard_user/', json=payload).text
    # else: # env == "production"
    #     pass
    # print("-"*150)

if __name__ == "__main__":

    run_tests(env="local")