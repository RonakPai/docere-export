'''
Functions for managing and connecting to tables in 
RDS databases.
'''

import os
import mysql.connector
import uuid
import csv
import argparse
import datetime

import keys
import augment_assignment

##################################### AWS SETUP #####################################

os.environ["AWS_ACCESS_KEY_ID"] = keys.AWS_ACCESS_KEY
os.environ["AWS_SECRET_ACCESS_KEY"] = keys.AWS_SECRET_ACCESS_KEY

############################### CREATE RDS CONNECTION ###############################

# create RDS DB connection
def create_connection(endpoint: str, 
                      username: str, 
                      password: str, 
                      database: str):
  return mysql.connector.connect(user=username,
                                 password=password,
                                 host=endpoint,
                                 database=database)

################################### CREATE TABLES ###################################

def create_assignment_table():

  rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
  rds_cursor = rds_connection.cursor()
  sql_query = '''CREATE TABLE IF NOT EXISTS assignments (
    assignment_id VARCHAR(255) NOT NULL,
    creator_username TEXT NOT NULL,
    assignment_title TEXT NOT NULL,
    subject TEXT NOT NULL,
    first_prompt TEXT NOT NULL,
    topic TEXT NOT NULL,
    question TEXT NOT NULL,
    lesson TEXT NOT NULL,
    student_age INT NOT NULL,
    max_attempts_before_answer_reveal INT NOT NULL,
    hide_assignment_answer BOOLEAN NOT NULL,
    disable_assignment_restart BOOLEAN NOT NULL,
    private_assignment BOOLEAN NOT NULL,
    lesson_length INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (assignment_id))'''
  rds_cursor.execute(sql_query)
  rds_cursor.close()
  rds_connection.commit()
  rds_connection.close()
  print("CREATED 'assignments' TABLE.")

def create_progress_table():
  
  rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
  rds_cursor = rds_connection.cursor()
  sql_query = '''CREATE TABLE IF NOT EXISTS progress (
    assignment_id VARCHAR(255) NOT NULL,
    student_username VARCHAR(255) NOT NULL,
    student_attempt INT NOT NULL,
    ai_augmented_lesson TEXT NOT NULL,
    history_as_string MEDIUMTEXT NOT NULL,
    num_attempts INT NOT NULL,
    num_total_iterations INT NOT NULL,
    lesson_completed BOOLEAN NOT NULL,
    final_report TEXT NOT NULL,
    progress_bar INT NOT NULL,
    start_time INT NOT NULL,
    end_time INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (assignment_id, student_username, student_attempt))'''
  rds_cursor.execute(sql_query)
  rds_cursor.close()
  rds_connection.commit()
  rds_connection.close()
  print("CREATED 'progress' TABLE.")

#################################### READ TABLES ####################################

def get_assignment_info(assignment_id: str,):

    output = {"assignment_id": assignment_id,
              "creator_username": "",
              "assignment_title": "",
              "subject": "",
              "first_prompt": "",
              "topic": "",
              "question": "",
              "lesson": "",
              "lesson_length": -1,
              "student_age": -1,
              "max_attempts_before_answer_reveal": -1,
              "hide_assignment_answer": False,
              "disable_assignment_restart": False,
              "private_assignment": False,
              "last_updated": ""}
    
    try:
        
        # get assignment info
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM assignments WHERE assignment_id=%s;"""
        params = [assignment_id,]
        rds_cursor.execute(sql_query, params)
        record = rds_cursor.fetchone()
        rds_cursor.close()
        rds_connection.close()
        output["assignment_id"] = record[0]
        output["creator_username"] = record[1]
        output["assignment_title"] = record[2]
        output["subject"] = record[3]
        output["first_prompt"] = record[4]
        output["topic"] = record[5]
        output["question"] = record[6]
        output["lesson"] = record[7]
        output["student_age"] = record[8]
        output["max_attempts_before_answer_reveal"] = record[9]
        output["hide_assignment_answer"] = record[10]
        output["disable_assignment_restart"] = record[11]
        output["private_assignment"] = record[12]
        output["lesson_length"] = record[13]
        output["last_updated"] = record[-1]

        # add assignment creator info
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM permissions WHERE username=%s;"""
        params = [output["creator_username"],]
        rds_cursor.execute(sql_query, params)
        record = rds_cursor.fetchone()
        rds_cursor.close()
        rds_connection.close()
        output["creator_name"] = record[1]

    except:
        pass
    
    return output

def update_lesson(assignment_id: str,
                  lesson: str):
    rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
    rds_cursor = rds_connection.cursor()
    sql_query = """UPDATE assignments
SET lesson=%s
WHERE assignment_id=%s;"""
    params = [lesson, assignment_id]
    rds_cursor.execute(sql_query, params)
    rds_cursor.close()
    rds_connection.commit()
    rds_connection.close()

    return {"assignment_id": assignment_id,}

def get_all_public_assignments(subject: str = "",
                               start_index: int = 0,
                               number_of_assignments_to_retrieve: float = float("inf"),):

    output = {"subject": subject,
              "assignment_list": [],}
    
    try:
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """\
WITH combined_assignments_and_progress AS (
    SELECT 
        a.assignment_id AS assignment_id,
        a.assignment_title AS assignment_title, 
        a.creator_username AS creator_username,
        perms.name AS creator_name,
        a.private_assignment AS private_assignment,
        a.subject AS subject,
        p.student_username AS student_username,
        a.last_updated AS last_updated
    FROM 
        assignments a
    LEFT JOIN 
        progress p ON a.assignment_id = p.assignment_id
    LEFT JOIN 
        permissions perms ON a.creator_username = perms.username
)
SELECT 
    assignment_id,
    assignment_title,
    creator_username,
    creator_name,
    subject,
    COUNT(DISTINCT student_username) AS num_students,
    last_updated
FROM 
    combined_assignments_and_progress
WHERE 
    {where_clause}
GROUP BY
    assignment_id, assignment_title, creator_username, creator_name, subject, last_updated
ORDER BY 
    last_updated DESC;"""
        if subject == "":
            where_clause = "private_assignment=FALSE"
            params = []
        else:
            where_clause = "private_assignment=FALSE AND\nsubject=%s"
            params = [subject,]
        rds_cursor.execute(sql_query.format(where_clause=where_clause),
                           params)
        records = rds_cursor.fetchall()
        rds_cursor.close()
        rds_connection.close()
        if number_of_assignments_to_retrieve == float("inf"):
            output["assignment_list"] = [{"assignment_id": record[0], 
                                          "assignment_title": record[1], 
                                          "creator_username": record[2],
                                          "creator_name": record[3],
                                          "subject": record[4],
                                          "num_students": record[5],
                                          "last_updated": str(record[-1])}
                                          for record in records]
        else:
            output["assignment_list"] = [{"assignment_id": record[0], 
                                          "assignment_title": record[1], 
                                          "creator_username": record[2],
                                          "creator_name": record[3],
                                          "subject": record[4],
                                          "num_students": record[5],
                                          "last_updated": str(record[-1])}
                                          for record in records[start_index:start_index+number_of_assignments_to_retrieve]]
    except:
        pass
    
    return output

def get_all_unjoined_public_assignments(username: str = "",
                                        subject: str = "",
                                        start_index: int = 0,
                                        number_of_assignments_to_retrieve: float = float("inf"),):
    
    output = {"username": username,
              "subject": subject,
              "assignment_list": [],}

    try:

        all_public_assignments = get_all_public_assignments(subject=subject)["assignment_list"]
        all_joined_assignment_ids = set([assignment["assignment_id"] for assignment in get_all_assigned_assignments(student_username=username)["assignment_list"]])

        all_unjoined_public_assignments = []
        for assignment in all_public_assignments:
            if assignment["assignment_id"] not in all_joined_assignment_ids:
                all_unjoined_public_assignments.append(assignment)
        if number_of_assignments_to_retrieve == float("inf"):
            output["assignment_list"] = all_unjoined_public_assignments
        else:
            output["assignment_list"] = all_unjoined_public_assignments[start_index:start_index+number_of_assignments_to_retrieve]

    except:
        pass

    return output
    
def get_all_created_assignments(creator_username: str,
                                start_index: int = 0,
                                number_of_assignments_to_retrieve: float = float("inf"),):

    output = {"creator_username": creator_username,
              "assignment_list": [],}
    
    try:
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """\
WITH combined_assignments_and_progress AS (
    SELECT 
        a.assignment_id AS assignment_id,
        a.assignment_title AS assignment_title, 
        a.creator_username AS creator_username,
        p.student_username AS student_username,
        a.last_updated AS last_updated
    FROM 
        assignments a
    LEFT JOIN 
        progress p ON a.assignment_id = p.assignment_id
)
SELECT 
    assignment_id,
    assignment_title,
    COUNT(DISTINCT student_username) AS num_students, 
    last_updated
FROM 
    combined_assignments_and_progress
WHERE 
    creator_username=%s
GROUP BY 
    assignment_id, assignment_title, last_updated
ORDER BY 
    last_updated DESC;"""
        params = [creator_username,]
        rds_cursor.execute(sql_query, params)
        records = rds_cursor.fetchall()
        rds_cursor.close()
        rds_connection.close()
        if number_of_assignments_to_retrieve == float("inf"):
            output["assignment_list"] = [{"assignment_id": record[0], 
                                          "assignment_title": record[1], 
                                          "num_students": record[2],
                                          "last_updated": str(record[-1])}
                                          for record in records]
        else:
            output["assignment_list"] = [{"assignment_id": record[0], 
                                          "assignment_title": record[1], 
                                          "num_students": record[2],
                                          "last_updated": str(record[-1])} 
                                          for record in records[start_index:start_index+number_of_assignments_to_retrieve]]
    except:
        pass
    
    return output

def get_num_created_assignments_last_thirty_days(creator_username: str,):

    output = {"creator_username": creator_username,
              "number_of_assignments": float('inf'),}
    
    try:
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        thirty_days_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        sql_query = """\
SELECT *
FROM 
    assignments
WHERE 
    creator_username=%s AND last_updated>=%s
ORDER BY 
    last_updated DESC;"""
        params = [creator_username, thirty_days_ago,]
        rds_cursor.execute(sql_query, params)
        records = rds_cursor.fetchall()
        rds_cursor.close()
        rds_connection.close()
        output["number_of_assignments"] = len(records)
    except:
        pass
    
    return output

def get_all_students(assignment_id: str,
                     start_index: int = 0,
                     number_of_students_to_retrieve: float = float("inf"),):

    output = {"assignment_id": assignment_id,
              "student_list": [],}
    
    try:
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM progress WHERE assignment_id=%s ORDER BY last_updated DESC;"""
        sql_query = """\
WITH combined_progress_and_student_names AS (
    SELECT 
        p.assignment_id as assignment_id,
        p.student_username as student_username,
        perms.name AS student_name,
        p.student_attempt as student_attempt,
        p.last_updated AS last_updated
    FROM 
        progress p
    LEFT JOIN 
        permissions perms ON p.student_username = perms.username
)
SELECT 
    *
FROM 
    combined_progress_and_student_names
WHERE 
    assignment_id = %s
ORDER BY 
    last_updated DESC;"""
        params = [assignment_id,]
        rds_cursor.execute(sql_query, params)
        records = rds_cursor.fetchall()
        rds_cursor.close()
        rds_connection.close()
        if number_of_students_to_retrieve == float("inf"):
            output["student_list"] = [{"student_username": record[1], 
                                        "student_name": record[2],
                                        "student_attempt": record[3], 
                                        "last_updated": str(record[-1])}
                                        for record in records]
        else:
            output["student_list"] = [{"student_username": record[1], 
                                        "student_name": record[2],
                                        "student_attempt": record[3], 
                                        "last_updated": str(record[-1])}
                                        for record in records[start_index:start_index+number_of_students_to_retrieve]]
    except:
        pass
    
    return output

def get_all_assigned_assignments(student_username: str,
                                 start_index: int = 0,
                                 number_of_assignments_to_retrieve: float = float("inf"),):
    
    output = {"student_username": student_username,
              "assignment_list": [],}
    
    try:
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()

        sql_query = """\
WITH combined_assignments_and_progress AS (
    SELECT 
        a.assignment_id AS assignment_id, 
        a.assignment_title AS assignment_title,
        perms.name AS creator_name,
        p.student_username AS student_username,
        p.student_attempt AS student_attempt,
        p.last_updated AS last_updated
    FROM 
        assignments a
    INNER JOIN 
        progress p ON a.assignment_id = p.assignment_id
    LEFT JOIN 
        permissions perms ON a.creator_username = perms.username
)
SELECT 
    *
FROM 
    combined_assignments_and_progress
WHERE 
    student_username = %s
ORDER BY 
    last_updated DESC;"""
        
        params = [student_username,]
        rds_cursor.execute(sql_query, params)
        records = rds_cursor.fetchall()
        rds_cursor.close()
        rds_connection.close()
        if number_of_assignments_to_retrieve == float("inf"):
            output["assignment_list"] = [{"assignment_id": record[0], 
                                          "assignment_title": record[1],
                                          "creator_name": record[2], 
                                          "student_attempt": record[4],
                                          "last_updated": str(record[-1])}
                                          for record in records]
        else:
            output["assignment_list"] = [{"assignment_id": record[0], 
                                          "assignment_title": record[1],
                                          "creator_name": record[2], 
                                          "student_attempt": record[4],
                                          "last_updated": str(record[-1])}
                                          for record in records[start_index:start_index+number_of_assignments_to_retrieve]]
    except:
        pass
    
    return output

def get_attempted_assignments_last_thirty_days(student_username: str,):

    output = {"student_username": student_username,
              "number_of_assignments": float('inf'),}
    
    try:
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        thirty_days_ago = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        sql_query = """\
SELECT assignment_id
FROM 
    progress
WHERE 
    student_username=%s AND last_updated>=%s
GROUP BY
    assignment_id
ORDER BY 
    last_updated DESC;"""
        params = [student_username, thirty_days_ago,]
        rds_cursor.execute(sql_query, params)
        records = rds_cursor.fetchall()
        rds_cursor.close()
        rds_connection.close()
        output["number_of_assignments"] = len(records)
    except:
        pass
    
    return output

def get_progress(assignment_id: str,
                 student_username: str,
                 student_attempt: int,):
    
    output = {"assignment_id": assignment_id,
              "student_username": student_username,
              "student_attempt": -1,
              "ai_augmented_lesson": "",
              "history_as_string": "",
              "num_attempts": -1,
              "num_total_iterations": -1,
              "lesson_completed": False,
              "progress_bar": 0,
              "start_time": 0,
              "end_time": 0,
              "last_updated": "",}
    
    try:
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM progress WHERE assignment_id=%s AND student_username=%s AND student_attempt=%s;"""
        params = [assignment_id, student_username, student_attempt,]
        rds_cursor.execute(sql_query, params)
        record = rds_cursor.fetchone()
        rds_cursor.close()
        rds_connection.close()
        output["assignment_id"] = record[0]
        output["student_username"] = record[1]
        output["student_attempt"] = record[2]
        output["ai_augmented_lesson"] = record[3]
        output["history_as_string"] = record[4]
        output["num_attempts"] = record[5]
        output["num_total_iterations"] = record[6]
        output["lesson_completed"] = record[7]
        output["progress_bar"] = record[9]
        output["start_time"] = record[10]
        output["end_time"] = record[11]
        output["last_updated"] = record[-1]
    except:
        pass
    
    return output

def get_in_progress_assignments(student_username: str,):
    
    output = {"student_username": student_username,
              "in_progress_assignments": [],}
    
    try:
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """\
WITH combined_assignments_and_progress AS (
    SELECT 
        a.assignment_id AS assignment_id,
        a.assignment_title AS assignment_title, 
        a.creator_username AS creator_username,
        perms.name AS creator_name,
        p.student_username AS student_username,
        p.student_attempt AS student_attempt,
        p.progress_bar AS progress_bar,
        p.last_updated AS last_updated
    FROM 
        assignments a
    INNER JOIN 
        progress p ON a.assignment_id = p.assignment_id
    LEFT JOIN 
        permissions perms ON a.creator_username = perms.username
)
SELECT 
    *
FROM 
    combined_assignments_and_progress
WHERE 
    student_username=%s AND
    progress_bar<100
ORDER BY 
    last_updated DESC;"""
        params = [student_username,]
        rds_cursor.execute(sql_query, params)
        records = rds_cursor.fetchall()
        rds_cursor.close()
        rds_connection.close()
        for record in records:
            assignment = {}
            assignment["assignment_id"] = record[0]
            assignment["assignment_title"] = record[1]
            assignment["creator_username"] = record[2]
            assignment["creator_name"] = record[3]
            assignment["student_attempt"] = record[5]
            assignment["progress_bar"] = record[6]
            assignment["last_updated"] = record[-1]
            output["in_progress_assignments"].append(assignment)
    except:
        pass
    
    return output

def get_num_attempts(assignment_id: str,
                     student_username: str,):
    
    try:
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM progress WHERE assignment_id=%s AND student_username=%s ORDER BY student_attempt DESC;"""
        params = [assignment_id, student_username,]
        rds_cursor.execute(sql_query, params)
        records = rds_cursor.fetchall()
        rds_cursor.close()
        rds_connection.close()
        return records[0][2]
    except:
        return 0

def get_final_report(assignment_id: str,
                     student_username: str,
                     student_attempt: str,):
    
    output = {"assignment_id": assignment_id,
              "student_username": student_username,
              "final_report": "",
              "last_updated": "",}
    
    try:
        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM progress WHERE assignment_id=%s AND student_username=%s AND student_attempt=%s;"""
        params = [assignment_id, student_username, student_attempt]
        rds_cursor.execute(sql_query, params)
        record = rds_cursor.fetchone()
        rds_cursor.close()
        rds_connection.close()
        output["assignment_id"] = record[0]
        output["student_username"] = record[1]
        output["final_report"] = record[8]
        output["last_updated"] = record[-1]
    except:
        pass
    
    return output
    

################################### UPDATE TABLES ###################################

def insert_assignment(creator_username: str,
                      assignment_id: str = "",
                      assignment_title: str = "",
                      subject: str = "",
                      first_prompt: str = "",
                      topic: str = "",
                      question: str = "",
                      lesson: str = "",
                      lesson_length: int = 30,
                      student_age: int = 21,
                      max_attempts_before_answer_reveal: int = 99999,
                      hide_assignment_answer: bool = False,
                      disable_assignment_restart: bool = False,
                      private_assignment: bool = False,):
    
    if assignment_id == "": # new assignment (create not update)
        assignment_id = str(uuid.uuid4())

    if first_prompt == "":
        first_prompt = augment_assignment.generate_first_prompt(topic=topic,
                                                                lesson=lesson,)

    rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
    rds_cursor = rds_connection.cursor()
    sql_query = """INSERT INTO assignments (assignment_id, creator_username, assignment_title, subject, first_prompt, topic, question, lesson, student_age, max_attempts_before_answer_reveal, hide_assignment_answer, disable_assignment_restart, private_assignment, lesson_length) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE 
creator_username=VALUES(creator_username),
assignment_title=VALUES(assignment_title),
subject=VALUES(subject),
first_prompt=VALUES(first_prompt),
topic=VALUES(topic),
question=VALUES(question),
lesson=VALUES(lesson),
student_age=VALUES(student_age),
max_attempts_before_answer_reveal=VALUES(max_attempts_before_answer_reveal),
hide_assignment_answer=VALUES(hide_assignment_answer),
disable_assignment_restart=VALUES(disable_assignment_restart),
private_assignment=VALUES(private_assignment),
lesson_length=VALUES(lesson_length);"""
    params = [assignment_id, creator_username, assignment_title, subject, first_prompt, topic, question, lesson, student_age, max_attempts_before_answer_reveal, hide_assignment_answer, disable_assignment_restart, private_assignment, lesson_length]
    rds_cursor.execute(sql_query, params)
    rds_cursor.close()
    rds_connection.commit()
    rds_connection.close()

    return {"assignment_id": assignment_id}

def update_progress(assignment_id: str,
                    student_username: str,
                    student_attempt: int,
                    ai_augmented_lesson: str = "",
                    history_as_string: str = "",
                    num_attempts: int = 0,
                    num_total_iterations: int = 0,
                    lesson_completed: bool = False,
                    final_report: str = "",
                    progress_bar: int = 0,
                    start_time: int = 0,
                    end_time: int = 0,):
    
    if ai_augmented_lesson == "":
        assignment_info = get_assignment_info(assignment_id=assignment_id)
        ai_augmented_lesson = augment_assignment.augment_lesson_on_lesson_join(topic=assignment_info['topic'],
                                                                               question=assignment_info['question'],
                                                                               lesson=assignment_info['lesson'],
                                                                               lesson_length=assignment_info['lesson_length'],
                                                                               student_age=assignment_info['student_age'],)
    
    rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
    rds_cursor = rds_connection.cursor()
    sql_query = """INSERT INTO progress (assignment_id, student_username, student_attempt, ai_augmented_lesson, history_as_string, num_attempts, num_total_iterations, lesson_completed, final_report, progress_bar, start_time, end_time) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
ON DUPLICATE KEY UPDATE 
ai_augmented_lesson=VALUES(ai_augmented_lesson),
history_as_string=VALUES(history_as_string),
num_attempts=VALUES(num_attempts),
num_total_iterations=VALUES(num_total_iterations),
lesson_completed=VALUES(lesson_completed),
final_report=VALUES(final_report),
progress_bar=VALUES(progress_bar),
start_time=VALUES(start_time),
end_time=VALUES(end_time);"""
    params = [assignment_id, student_username, student_attempt, ai_augmented_lesson, history_as_string, num_attempts, num_total_iterations, lesson_completed, final_report, progress_bar, start_time, end_time]
    rds_cursor.execute(sql_query, params)
    rds_cursor.close()
    rds_connection.commit()
    rds_connection.close()

    return {"assignment_id": assignment_id,
            "student_username": student_username,
            "student_attempt": student_attempt}

def insert_final_report(assignment_id: str,
                        student_username: str,
                        student_attempt: int,
                        final_report: str = "",):
    rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
    rds_cursor = rds_connection.cursor()
    sql_query = """UPDATE progress
SET final_report=%s
WHERE assignment_id=%s AND student_username=%s AND student_attempt=%s;"""
    params = [final_report, assignment_id, student_username, student_attempt,]
    rds_cursor.execute(sql_query, params)
    rds_cursor.close()
    rds_connection.commit()
    rds_connection.close()

    return {"assignment_id": assignment_id,
            "student_username": student_username,
            "student_attempt": student_attempt}

############################### DELETE RECORDS/TABLES ###############################

# drop table in RDS DB
def drop_table(rds_table_name: str):
  rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
  rds_cursor = rds_connection.cursor()
  rds_cursor.execute('DROP TABLE IF EXISTS {};'.format(rds_table_name))
  rds_cursor.close()
  rds_connection.commit()
  rds_connection.close()
  print("DROPPED '{}' TABLE.".format(rds_table_name))

# drop assignment
def delete_assignment(assignment_id: str):
  rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
  rds_cursor = rds_connection.cursor()
  sql_query = "DELETE FROM assignments WHERE assignment_id=%s;"
  params = [assignment_id,]
  rds_cursor.execute(sql_query, params)
  sql_query = "DELETE FROM progress WHERE assignment_id=%s;"
  params = [assignment_id,]
  rds_cursor.execute(sql_query, params)
  rds_cursor.close()
  rds_connection.commit()
  rds_connection.close()
  print("DELETED ASSIGNMENT '{}'.".format(assignment_id))

# drop student progress
def delete_progress(assignment_id: str,
                    student_username: str,
                    student_attempt: int,):
  rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
  rds_cursor = rds_connection.cursor()
  sql_query = "DELETE FROM progress WHERE assignment_id=%s AND student_username=%s AND student_attempt=%s;"
  params = [assignment_id, student_username, student_attempt]
  rds_cursor.execute(sql_query, params)
  rds_cursor.close()
  rds_connection.commit()
  rds_connection.close()
  print("DELETED '{}' FROM ASSIGNMENT '{}'.".format(student_username, assignment_id))

#####################################################################################

def get_table(assignments_filepath: str = "assignments.csv",
               progress_filepath: str = "progress.csv"):
    
    # get assignments table

    try:

        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM assignments ORDER BY last_updated ASC;"""
        rds_cursor.execute(sql_query)
        records = rds_cursor.fetchall()

        with open(assignments_filepath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([desc[0] for desc in rds_cursor.description])
            csv_writer.writerows(records)

        rds_cursor.close()
        rds_connection.close()

    except:

        pass

    # get progress table

    try:

        rds_connection = create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM progress ORDER BY last_updated ASC;"""
        rds_cursor.execute(sql_query)
        records = rds_cursor.fetchall()

        with open(progress_filepath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([desc[0] for desc in rds_cursor.description])
            csv_writer.writerows(records)

        rds_cursor.close()
        rds_connection.close()

    except:
        
        pass

def main():

    parser = argparse.ArgumentParser(description="Assignments & Progress Management Script")
    parser.add_argument("--get_table", action="store_true", help="Write the contents of the `assignments` table to assignments.csv and `progress` table to progress.csv.")
    args = parser.parse_args()
    
    if args.get_table:

        get_table()

    else:

        print("-"*150)
    
        for rds_table_name in ['assignments', 'progress']:
            user_response = input("DELETE '{}' TABLE FROM RDS DATABASE? (yes/no): ".format(rds_table_name))
            if user_response == 'yes':
                drop_table(rds_table_name=rds_table_name)
            elif user_response == 'no':
                print("NO ACTION TO '{}' TABLE.".format(rds_table_name))
            else:
                print("INVALID RESPONSE RECEIEVED. NO ACTION TO '{}' TABLE.".format(rds_table_name))
            print("-  "*50)

        create_assignment_table()
        create_progress_table()

if __name__ == "__main__":
    
    main()