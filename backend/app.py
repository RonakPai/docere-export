from flask import Flask, request
from flask_cors import CORS
import json
import re
import csv

import genai_classroom
import genai_presenter
import rds_management
import quota_management
import permissions_management
import augment_assignment
import onboard_beta_testers

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST', 'FETCH'])
def health_check():
    return json.dumps({"Response": "Success"})

@app.route('/onboard_user/', methods=['POST'])
def onboard_user():

    data = request.get_json()
    username = data.get('username', '')
    name = data.get('name', '')
    organization = data.get('organization', '')
    subscription_tier = data.get('subscription_tier', '') # ['free', 'student', 'teacher', 'school']

    user_permissions = permissions_management.get_permissions(username=username)
    
    valid_subscription_tiers = set(['free', 'student', 'teacher', 'school'])
    if subscription_tier == '':
        if user_permissions['active']:
            subscription_tier = user_permissions['subscription_tier']
        else: # user account not active
            subscription_tier = "free"
    elif subscription_tier not in valid_subscription_tiers:
        return {"status": "Error.", 
                "message": "Invalid subscription tier: '{}'. Select from the following subscription tier options: {}.".format(subscription_tier, valid_subscription_tiers)}
        
    # request validation + execution
    onboarded = False
    if subscription_tier == 'free' and (user_permissions['active'] == False or 
                                        user_permissions['subscription_tier'] != "free"):
        quota_management.set_free_tier_quotas(username=username)
        permissions_management.set_free_tier_permissions(username=username,
                                                         name=name,
                                                         organization=organization)
        onboarded = True
        print("ONBOARDED '{}'.".format(username))
    elif subscription_tier == 'student' and (user_permissions['active'] == False or 
                                             user_permissions['subscription_tier'] != "student"):
        quota_management.set_student_tier_quotas(username=username)
        permissions_management.set_student_tier_permissions(username=username,
                                                            name=name,
                                                            organization=organization)
        onboarded = True
        print("ONBOARDED '{}'.".format(username))
    elif subscription_tier == 'teacher' and (user_permissions['active'] == False or 
                                             user_permissions['subscription_tier'] != "teacher"):
        quota_management.set_teacher_tier_quotas(username=username)
        permissions_management.set_teacher_tier_permissions(username=username,
                                                            name=name,
                                                            organization=organization)
        onboarded = True
        print("ONBOARDED '{}'.".format(username))
    elif subscription_tier == 'school' and (user_permissions['active'] == False or 
                                            user_permissions['subscription_tier'] != "school"):
        quota_management.set_school_tier_quotas(username=username)
        permissions_management.set_school_tier_permissions(username=username,
                                                           name=name,
                                                           organization=organization)
        onboarded = True
        print("ONBOARDED '{}'.".format(username))
    
    return json.dumps({"username": username,
                       "valid_user": True,
                       "onboarded": onboarded}) # IMPORTANT: 'onboarded' value will be False if user was PREVIOUSLY ALREADY onboarded

@app.route('/offboard_user/', methods=['POST'])
def offboard_user():

    data = request.get_json()
    username = data.get('username', '')

    # # remove assignments created by this user
    # active_assignments = rds_management.get_all_created_assignments(creator_username=username)
    # for assignment_id in [t[0] for t in active_assignments['assignment_list']]:
    #     rds_management.delete_assignment(assignment_id=assignment_id)

    # # remove any progress made by this user on assignments
    # active_progress = rds_management.get_all_assigned_assignments(student_username=username)
    # for assignment_id in [t[0] for t in active_progress['assignment_list']]:
    #     rds_management.delete_progress(assignment_id=assignment_id, student_username=username)

    # remove quotas set for this user
    quota_management.delete_quotas(username=username)

    # remove permissions for this user
    permissions_management.delete_permissions(username=username)

    print("OFFBOARDED '{}'.".format(username))
    return json.dumps({"username": username})

@app.route('/get_user_basic_info/', methods=['POST'])
def get_user_basic_info():

    data = request.get_json()
    username = data.get('username', '')

    return json.dumps(permissions_management.get_user_basic_info(username=username))

@app.route('/update_name/', methods=['POST'])
def update_name():

    data = request.get_json()
    username = data.get('username', '')
    name = data.get('name', '')

    return json.dumps(permissions_management.update_name(username=username,
                                                         name=name))

@app.route('/update_organization/', methods=['POST'])
def update_organization():

    data = request.get_json()
    username = data.get('username', '')
    organization = data.get('organization', '')

    return json.dumps(permissions_management.update_organization(username=username,
                                                                 organization=organization))

@app.route('/create_assignment/', methods=['POST'])
def create_assignment():

    data = request.get_json()
    creator_username = data.get('creator_username', '')
    assignment_id = data.get('assignment_id', '') # if set, will UPDATE assignment
    assignment_title = data.get('assignment_title', 'Untitled')
    subject = data.get('subject', 'Other')
    topic = data.get('topic', '')
    lesson = data.get('lesson', '')
    lesson_length = data.get('lesson_length', 30) # minutes
    first_prompt = data.get('first_prompt', "Let's discuss the following topic/question:\n\n{}".format(topic))
    student_age = data.get('student_age', 21)
    hide_assignment_answer = data.get('hide_assignment_answer', False)
    disable_assignment_restart = data.get('disable_assignment_restart', False)
    private_assignment = data.get('private_assignment', False)

    # request validation
    if creator_username == "":
        return {"status": "Error.", "message": "Assignment creator's username missing from assignment creation request."}
    
    # check quotas
    if not quota_management.check_assignments_created_quota(creator_username=creator_username):
        return {"status": "Error.", "message": "User '{}' has reached their assignment creation quota.".format(creator_username)}
    
    # check permissions
    user_permissions = permissions_management.get_permissions(username=creator_username)
    if hide_assignment_answer and not user_permissions['allow_hide_assignment_answer']:
        return {"status": "Error.", "message": "User '{}' is not permitted to hide assignment answers.".format(creator_username)}
    if disable_assignment_restart and not user_permissions['allow_disable_assignment_restart']:
        return {"status": "Error.", "message": "User '{}' is not permitted to disable assignment restart.".format(creator_username)}
    if private_assignment and not user_permissions['allow_private_assignment']:
        return {"status": "Error.", "message": "User '{}' is not permitted to create private assignments.".format(creator_username)}
    
    # calculate max_attempts_before_answer_reveal based on desired lesson length
    max_attempts_before_answer_reveal = max(1, lesson_length // 10)

    response = rds_management.insert_assignment(creator_username=creator_username,
                                                assignment_title=assignment_title,
                                                assignment_id=assignment_id,
                                                subject=subject,
                                                first_prompt=first_prompt,
                                                topic=topic,
                                                lesson=lesson,
                                                lesson_length=lesson_length,
                                                student_age=student_age,
                                                max_attempts_before_answer_reveal=max_attempts_before_answer_reveal,
                                                hide_assignment_answer=hide_assignment_answer,
                                                disable_assignment_restart=disable_assignment_restart,
                                                private_assignment=private_assignment)
    return json.dumps(response)

@app.route('/ai_augment_uploaded_lesson_contents/', methods=['POST'])
def ai_augment_uploaded_lesson_contents():

    data = request.get_json()
    topic = data.get('topic', '')
    question = data.get('question', '')
    lesson = data.get('lesson', '') # only field required
    lesson_length = data.get('lesson_length', 30) # minutes
    student_age = data.get('student_age', 21)

    return augment_assignment.augment_lesson(topic=topic,
                                             question=question,
                                             lesson=lesson,
                                             lesson_length=lesson_length,
                                             student_age=student_age)

@app.route('/generate_assignment_contents/', methods=['POST'])
def generate_assignment_contents():

    data = request.get_json()
    lesson_contents = data.get('lesson_contents', '')

    return augment_assignment.generate_assignment_contents(lesson_contents=lesson_contents,)

@app.route('/update_lesson/', methods=['POST'])
def update_lesson():

    data = request.get_json()
    assignment_id = data.get('assignment_id', '')
    updated_lesson = data.get('updated_lesson', '')

    return json.dumps(rds_management.update_lesson(assignment_id=assignment_id,
                                                   lesson=updated_lesson))

@app.route('/delete_assignment/', methods=['POST'])
def delete_assignment():

    data = request.get_json()
    assignment_id = data.get('assignment_id', '')

    _ = rds_management.delete_assignment(assignment_id=assignment_id)
    return json.dumps({"assignment_id": assignment_id})
    
@app.route('/join_assignment/', methods=['POST'])
def join_assignment():

    data = request.get_json()
    assignment_id = data.get('assignment_id', '')
    student_username = data.get('student_username', '')

    # request validation
    if student_username == "":
        return {"status": "Error.", "message": "Student username missing from assignment join request."}
    if assignment_id == "" or rds_management.get_assignment_info(assignment_id=assignment_id)["creator_username"] == "":
        return {"status": "Error.", "message": "Invalid Assignment ID."}
    
    current_students = [student["student_username"] for student in rds_management.get_all_students(assignment_id=assignment_id)['student_list']]
    if student_username in current_students:
        return {"status": "Error.", "message": "User '{}' has already joined assignment '{}'.".format(student_username, assignment_id)}
    
    if not quota_management.check_assignments_joined_quota(student_username=student_username, assignment_id=assignment_id):
        return {"status": "Error.", "message": "User '{}' has reached their assignment join quota.".format(student_username)}
    
    if not quota_management.check_num_students_quota(assignment_id=assignment_id, student_username=student_username):
        return {"status": "Error.", "message": "Assignment '{}' has reached the maximum allowed number of students.".format(assignment_id)}

    response = rds_management.update_progress(student_username=student_username,
                                              assignment_id=assignment_id,
                                              student_attempt=1)
    return json.dumps(response)

@app.route('/restart_assignment/', methods=['POST'])
def restart_assignment():

    data = request.get_json()
    assignment_id = data.get('assignment_id', '')
    student_username = data.get('student_username', '')
    student_attempt = data.get('student_attempt', -1)

    # request validation
    if assignment_id == "" or student_username == "" or student_attempt == -1:
        return {"status": "Error.", "message": "Restart assignment request missing assignment ID, student username, or attempt number."}
    
    # check if assignment restart allowed
    assignment_info = rds_management.get_assignment_info(assignment_id=assignment_id)
    if assignment_info['disable_assignment_restart']:
        return {"status": "Error.", "message": "Assignment '{}' cannot be restarted.".format(assignment_id)}
    
    current_progress = rds_management.get_progress(assignment_id=assignment_id,
                                                   student_username=student_username,
                                                   student_attempt=student_attempt)
    response = rds_management.update_progress(student_username=student_username,
                                              assignment_id=assignment_id,
                                              student_attempt=student_attempt,
                                              ai_augmented_lesson=current_progress['ai_augmented_lesson'])
    return json.dumps(response)

@app.route('/delete_progress/', methods=['POST'])
def delete_progress():

    data = request.get_json()
    assignment_id = data.get('assignment_id', '')
    student_username = data.get('assignment_id', '')
    student_attempt = data.get('student_attempt', -1)

    _ = rds_management.delete_progress(assignment_id=assignment_id, 
                                       student_username=student_username,
                                       student_attempt=student_attempt)
    return json.dumps({"assignment_id": assignment_id,
                       "student_username": student_username,
                       "student_attempt": student_attempt})

@app.route('/get_assignment_info/', methods=['POST'])
def get_assignment_info():

    data = request.get_json()
    assignment_id = data.get('assignment_id', '')

    # request validation
    if assignment_id == "":
        return {"status": "Error.", "message": "Assignment information retrieval request missing assignment ID."}

    assignment_info = rds_management.get_assignment_info(assignment_id=assignment_id)
    assignment_info['last_updated'] = str(assignment_info['last_updated'])
    return json.dumps(assignment_info)

@app.route('/get_all_public_assignments/', methods=['POST'])
def get_all_public_assignments():

    data = request.get_json()
    subject = data.get('subject', '')
    start_index = data.get('start_index', 0)
    num_assignments_to_retrieve = data.get('num_assignments_to_retrieve', float("inf"))

    response = rds_management.get_all_public_assignments(subject=subject,
                                                         start_index=start_index,
                                                         number_of_assignments_to_retrieve=num_assignments_to_retrieve)
    return json.dumps(response)

@app.route('/get_all_unjoined_public_assignments/', methods=['POST'])
def get_all_unjoined_public_assignments():

    data = request.get_json()
    username = data.get('username', '')
    subject = data.get('subject', '')
    start_index = data.get('start_index', 0)
    num_assignments_to_retrieve = data.get('num_assignments_to_retrieve', float("inf"))

    response = rds_management.get_all_unjoined_public_assignments(username=username,
                                                                  subject=subject,
                                                                  start_index=start_index,
                                                                  number_of_assignments_to_retrieve=num_assignments_to_retrieve)
    return json.dumps(response)

@app.route('/get_all_created_assignments/', methods=['POST'])
def get_all_created_assignments():

    data = request.get_json()
    creator_username = data.get('creator_username', '')
    start_index = data.get('start_index', 0)
    num_assignments_to_retrieve = data.get('num_assignments_to_retrieve', float("inf"))

    # request validation
    if creator_username == "":
        return {"status": "Error.", "message": "Get all created assignments request missing creator username."}

    response = rds_management.get_all_created_assignments(creator_username=creator_username,
                                                          start_index=start_index,
                                                          number_of_assignments_to_retrieve=num_assignments_to_retrieve)
    return json.dumps(response)

@app.route('/get_all_assigned_assignments/', methods=['POST'])
def get_all_assigned_assignments():

    data = request.get_json()
    student_username = data.get('student_username', '')
    start_index = data.get('start_index', 0)
    num_assignments_to_retrieve = data.get('num_assignments_to_retrieve', float("inf"))

    # request validation
    if student_username == "":
        return {"status": "Error.", "message": "Get all joined assignments missing student username."}

    response = rds_management.get_all_assigned_assignments(student_username=student_username,
                                                           start_index=start_index,
                                                           number_of_assignments_to_retrieve=num_assignments_to_retrieve)
    return json.dumps(response)

@app.route('/get_in_progress_assignments/', methods=['POST'])
def get_in_progress_assignments():

    data = request.get_json()
    student_username = data.get('student_username', '')

    # request validation
    if student_username == "":
        return {"status": "Error.", "message": "In-progress assignments retrieval request missing student username."}
    
    in_progress_assignments = rds_management.get_in_progress_assignments(student_username=student_username)
    for i in range(len(in_progress_assignments['in_progress_assignments'])):
        in_progress_assignments['in_progress_assignments'][i]['last_updated'] = str(in_progress_assignments['in_progress_assignments'][i]['last_updated'])
    return json.dumps(in_progress_assignments)

@app.route('/get_all_students/', methods=['POST'])
def get_all_students():

    data = request.get_json()
    assignment_id = data.get('assignment_id', '')
    start_index = data.get('start_index', 0)
    num_students_to_retrieve = data.get('num_students_to_retrieve', float("inf"))

    response = rds_management.get_all_students(assignment_id=assignment_id,
                                               start_index=start_index,
                                               number_of_students_to_retrieve=num_students_to_retrieve)
    return json.dumps(response)

@app.route('/get_num_attempts/', methods=['POST'])
def get_num_attempts():

    data = request.get_json()
    assignment_id = data.get('assignment_id', '')
    student_username = data.get('student_username', '')

    # request validation
    if assignment_id == "" or student_username == "":
        return {"status": "Error.", "message": "Number of attempts retrieval request missing assigment ID or username."}
    
    return rds_management.get_num_attempts(assignment_id=assignment_id,
                                           student_username=student_username)

@app.route('/get_assignment_progress/', methods=['POST'])
def get_assignment_progress():

    data = request.get_json()
    assignment_id = data.get('assignment_id', '')
    student_username = data.get('student_username', '')
    student_attempt = data.get('student_attempt', -1)

    # request validation
    if assignment_id == "" or student_username == "" or student_attempt == -1:
        return {"status": "Error.", "message": "Assignment progress retrieval request missing assignment ID, student username, or attempt number."}
    
    progress = rds_management.get_progress(assignment_id=assignment_id,
                                           student_username=student_username,
                                           student_attempt=student_attempt)
    progress['last_updated'] = str(progress['last_updated'])
    return json.dumps(progress)

@app.route('/get_next_question/', methods=['POST'])
def get_next_question():
    
    data = request.get_json()
    assignment_id = data.get('assignment_id', '')
    student_username = data.get('student_username', '')
    student_answer = data.get('student_answer', '')
    student_attempt = data.get('student_attempt', '')

    # request validation
    if assignment_id == "" or student_username == "":
        return {"status": "Error.", "message": "Next question generation request missing assignment ID or student username."}

    actor, next_question, lesson_completed, progress_bar = genai_classroom.get_next_question_helper(assignment_id=assignment_id,
                                                                                      student_username=student_username,
                                                                                      student_answer=student_answer,
                                                                                      student_attempt=student_attempt)

    return json.dumps({"actor": actor, # will be "TEACHER" or "STUDENT"
                       "next_question": next_question,
                       "lesson_completed": lesson_completed, # boolean value
                       "progress_bar": progress_bar, # integer from 0 to 100 (inclusive)
                       })

@app.route('/get_next_question_for_lesson_simulation/', methods=['POST'])
def get_next_question_for_lesson_simulation():

    data = request.get_json()
    topic = data.get('topic', '')
    question = data.get('question', '')
    lesson = data.get('lesson', '')
    student_answer = data.get('student_answer', '')
    history_as_string = data.get('history_as_string', '')
    previous_progress = data.get('previous_progress', '')
    num_attempts = data.get('num_attempts', 0)
    student_age = data.get('student_age', 21)
    max_attempts_before_answer_reveal = data.get('max_attempts_before_answer_reveal', 2)

    # request validation
    if topic == "" or lesson == "":
        return {"status": "Error.", "message": "Next question generation (for simulation) request missing topic or lesson."}

    actor, next_question, lesson_completed, progress_bar, num_attempts, history_as_string = genai_classroom.get_next_question_for_simulation_helper(topic=topic,
                                                                                                                                                    question=question,
                                                                                                                                                    lesson=lesson,
                                                                                                                                                    student_answer=student_answer,
                                                                                                                                                    history_as_string=history_as_string,
                                                                                                                                                    previous_progress=previous_progress,
                                                                                                                                                    num_attempts=num_attempts,
                                                                                                                                                    student_age=student_age,
                                                                                                                                                    max_attempts_before_answer_reveal=max_attempts_before_answer_reveal)

    return json.dumps({"actor": actor, # will be "TEACHER" or "STUDENT"
                       "next_question": next_question,
                       "lesson_completed": lesson_completed, # boolean value
                       "progress_bar": progress_bar, # integer from 0 to 100 (inclusive)
                       "num_attempts": num_attempts, # number of attempts student has made to answer current line of questioning
                       "history_as_string": history_as_string, # lesson presentation history
                       })

@app.route('/get_ai_presenter_answer/', methods=['POST'])
def get_ai_presenter_answer():
    
    data = request.get_json()
    assignment_id = data.get('assignment_id', '')
    topic = data.get('topic', '')
    question = data.get('question', '') # question inputted on lesson creation
    lesson = data.get('lesson', '')
    requester_username = data.get('username', '')
    question_for_ai_presenter = data.get('next_question', '') # question for AI-Presenter to answer
    correct = data.get('correct', True)

    # request validation
    if requester_username == "":
        return {"status": "Error.", "message": "AI-Presenter answer generation request missing requester username."}
    if assignment_id == "" and (topic == "" or lesson == ""):
        return {"status": "Error.", "message": "AI-Presenter answer generation request missing parameters. Please input either (A) an assignment ID or (B) both a topic and corresponding lesson."}
    if question_for_ai_presenter == "":
        return {"status": "Error.", "message": "AI-Presenter answer generation request missing question for AI-Presenter to answer."}
    
    # check permissions
    user_permissions = permissions_management.get_permissions(username=requester_username)
    if not user_permissions['enable_ai_generated_assignment_simulation']:
        return {"status": "Error.", "message": "User '{}' is not permitted to access the AI-Presenter.".format(requester_username)}

    return genai_presenter.ai_presenter_response_helper(assignment_id=assignment_id,
                                                        topic=topic,
                                                        question=question,
                                                        lesson=lesson,
                                                        question_for_ai_presenter=question_for_ai_presenter,
                                                        correct=correct)

@app.route('/generate_assignment_report/', methods=['POST'])
def generate_assignment_report():

    data = request.get_json()
    assignment_id = data.get('assignment_id', '')
    student_username = data.get('student_username', '')
    student_attempt = data.get('student_attempt', -1)

    # request validation
    if assignment_id == "" or student_username == "" or student_attempt == -1:
        return {"status": "Error.", "message": "Assignment report generation request missing assignment ID, student username, or attempt number."}
    
    # check permissions
    user_permissions = permissions_management.get_permissions(username=student_username)
    if not user_permissions['enable_ai_generated_final_report']:
        return {"status": "Error.", "message": "User '{}' is not permitted to access the AI-Generated report.".format(student_username)}
    
    return augment_assignment.get_assignment_report(assignment_id=assignment_id, 
                                                    student_username=student_username, 
                                                    student_attempt=student_attempt)

@app.route('/regenerate_assignment/', methods=['POST'])
def regenerate_assignment():

    data = request.get_json()
    assignment_id = data.get('assignment_id', '')
    student_username = data.get('student_username', '')
    student_attempt = data.get('student_attempt', -1)
    lesson_length = data.get('lesson_length', 30) # minutes

    # request validation
    if assignment_id == "" or student_username == "" or student_attempt == -1:
        return {"status": "Error.", "message": "Assignment report generation request missing assignment ID, student username, or attempt number."}
    
    # check permissions
    user_permissions = permissions_management.get_permissions(username=student_username)
    if not user_permissions['enable_regenerate_assignment_based_on_final_report']:
        return {"status": "Error.", "message": "User '{}' is not permitted to regenerate assignments based on AI-Generated reports.".format(student_username)}
    
    return json.dumps(augment_assignment.regenerate_lesson(assignment_id=assignment_id, 
                                                           student_username=student_username, 
                                                           student_attempt=student_attempt,
                                                           lesson_length=lesson_length))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)