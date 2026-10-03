'''
Functions for managing user quotas.
'''

import csv
import argparse

import keys
import rds_management

################################### CREATE TABLES ###################################

def create_quotas_table():
  
  rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
  rds_cursor = rds_connection.cursor()
  sql_query = '''CREATE TABLE IF NOT EXISTS quotas (
    username VARCHAR(255) NOT NULL,
    assignments_created_quota INT NOT NULL,
    assignments_joined_quota INT NOT NULL,
    num_students_per_private_assignment_quota INT NOT NULL,
    num_questions_per_assignment_quota INT NOT NULL,
    num_iterations_per_assignment_quota INT NOT NULL,
    num_attempts_per_assignment_quota INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (username))'''
  rds_cursor.execute(sql_query)
  rds_cursor.close()
  rds_connection.commit()
  rds_connection.close()
  print("CREATED 'quotas' TABLE.")

#################################### READ TABLES ####################################

def get_quotas(username: str,):
   
    output = {"username": username,
              "assignments_created_quota": -1,
              "assignments_joined_quota": -1,
              "num_students_per_private_assignment_quota": -1,
              "num_questions_per_assignment_quota": -1,
              "num_iterations_per_assignment_quota": -1,
              "num_attempts_per_assignment_quota": -1}
    
    try:
        rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM quotas WHERE username=%s;"""
        params = [username,]
        rds_cursor.execute(sql_query, params)
        record = rds_cursor.fetchone()
        rds_cursor.close()
        rds_connection.close()
        output["username"] = record[0]
        output["assignments_created_quota"] = record[1]
        output["assignments_joined_quota"] = record[2]
        output["num_students_per_private_assignment_quota"] = record[3]
        output["num_questions_per_assignment_quota"] = record[4]
        output["num_iterations_per_assignment_quota"] = record[5]
        output["num_attempts_per_assignment_quota"] = record[6]
    except:
        pass
    
    return output

def check_assignments_created_quota(creator_username: str):
    assignments_created_quota = get_quotas(username=creator_username)['assignments_created_quota']
    num_assignments_created = rds_management.get_num_created_assignments_last_thirty_days(creator_username=creator_username)['number_of_assignments']
    return num_assignments_created < assignments_created_quota

def check_assignments_joined_quota(student_username: str,
                                   assignment_id: str):

    assignments_joined_quota = get_quotas(username=student_username)['assignments_joined_quota']
    assignments_joined = rds_management.get_all_assigned_assignments(student_username=student_username)['assignment_list']
    if assignment_id in assignments_joined:
        return True
    else:
        num_assignments_attempted = rds_management.get_attempted_assignments_last_thirty_days(student_username=student_username)['number_of_assignments']
        return num_assignments_attempted < assignments_joined_quota
    
def check_num_students_quota(assignment_id: str,
                             student_username: str):
    
    assignment_info = rds_management.get_assignment_info(assignment_id=assignment_id)
    if assignment_info['private_assignment'] == False:
        return True
    
    num_students_per_private_assignment_quota = get_quotas(username=assignment_info['creator_username'])['num_students_per_private_assignment_quota']
    students_in_assignment = rds_management.get_all_students(assignment_id=assignment_id)['student_list']
    if student_username in students_in_assignment:
        return True
    else:
        return len(students_in_assignment) < num_students_per_private_assignment_quota
    
def get_num_questions_per_assignment_quota(creator_username: str):
    return get_quotas(username=creator_username)['num_questions_per_assignment_quota']

def get_num_iterations_per_assignment_quota(student_username: str):
    return get_quotas(username=student_username)['num_iterations_per_assignment_quota']

def get_num_attempts_per_assignment_quota(student_username: str):
    return get_quotas(username=student_username)['num_attempts_per_assignment_quota']
    
################################### UPDATE TABLES ###################################

# def set_beta_tester_quotas(username: str,):
   
#     assignments_created_quota = 10
#     assignments_joined_quota = 10
#     num_students_per_private_assignment_quota = 10000
#     num_questions_per_assignment_quota = 10000
#     num_iterations_per_assignment_quota = 10000

#     return set_quotas(username=username,
#                       assignments_created_quota=assignments_created_quota,
#                       assignments_joined_quota=assignments_joined_quota,
#                       num_students_per_private_assignment_quota=num_students_per_private_assignment_quota,
#                       num_questions_per_assignment_quota=num_questions_per_assignment_quota,
#                       num_iterations_per_assignment_quota=num_iterations_per_assignment_quota)

def set_free_tier_quotas(username: str,):
   
    assignments_created_quota = 3
    assignments_joined_quota = 3
    num_students_per_private_assignment_quota = 0 # private assignments disabled
    num_questions_per_assignment_quota = 10000 # unused feature
    num_iterations_per_assignment_quota = 10000
    num_attempts_per_assignment_quota = 2

    return set_quotas(username=username,
                      assignments_created_quota=assignments_created_quota,
                      assignments_joined_quota=assignments_joined_quota,
                      num_students_per_private_assignment_quota=num_students_per_private_assignment_quota,
                      num_questions_per_assignment_quota=num_questions_per_assignment_quota,
                      num_iterations_per_assignment_quota=num_iterations_per_assignment_quota,
                      num_attempts_per_assignment_quota=num_attempts_per_assignment_quota,)

def set_student_tier_quotas(username: str,):
   
    assignments_created_quota = 30
    assignments_joined_quota = 30
    num_students_per_private_assignment_quota = 1
    num_questions_per_assignment_quota = 10000 # unused feature
    num_iterations_per_assignment_quota = 10000
    num_attempts_per_assignment_quota = 6

    return set_quotas(username=username,
                      assignments_created_quota=assignments_created_quota,
                      assignments_joined_quota=assignments_joined_quota,
                      num_students_per_private_assignment_quota=num_students_per_private_assignment_quota,
                      num_questions_per_assignment_quota=num_questions_per_assignment_quota,
                      num_iterations_per_assignment_quota=num_iterations_per_assignment_quota,
                      num_attempts_per_assignment_quota=num_attempts_per_assignment_quota,)

def set_teacher_tier_quotas(username: str,):
   
    assignments_created_quota = 30
    assignments_joined_quota = 30
    num_students_per_private_assignment_quota = 100000000 # unlimited
    num_questions_per_assignment_quota = 10000 # unused feature
    num_iterations_per_assignment_quota = 10000
    num_attempts_per_assignment_quota = 6

    return set_quotas(username=username,
                      assignments_created_quota=assignments_created_quota,
                      assignments_joined_quota=assignments_joined_quota,
                      num_students_per_private_assignment_quota=num_students_per_private_assignment_quota,
                      num_questions_per_assignment_quota=num_questions_per_assignment_quota,
                      num_iterations_per_assignment_quota=num_iterations_per_assignment_quota,
                      num_attempts_per_assignment_quota=num_attempts_per_assignment_quota,)

def set_school_tier_quotas(username: str,):
   
    assignments_created_quota = 1000
    assignments_joined_quota = 1000
    num_students_per_private_assignment_quota = 100000000 # unlimited
    num_questions_per_assignment_quota = 10000 # unused feature
    num_iterations_per_assignment_quota = 10000
    num_attempts_per_assignment_quota = 6

    return set_quotas(username=username,
                      assignments_created_quota=assignments_created_quota,
                      assignments_joined_quota=assignments_joined_quota,
                      num_students_per_private_assignment_quota=num_students_per_private_assignment_quota,
                      num_questions_per_assignment_quota=num_questions_per_assignment_quota,
                      num_iterations_per_assignment_quota=num_iterations_per_assignment_quota,
                      num_attempts_per_assignment_quota=num_attempts_per_assignment_quota,)

def set_quotas(username: str,
               assignments_created_quota: int,
               assignments_joined_quota: int,
               num_students_per_private_assignment_quota: int,
               num_questions_per_assignment_quota: int,
               num_iterations_per_assignment_quota: int,
               num_attempts_per_assignment_quota: int,):
    
    rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
    rds_cursor = rds_connection.cursor()
    sql_query = """INSERT INTO quotas (username, assignments_created_quota, assignments_joined_quota, num_students_per_private_assignment_quota, num_questions_per_assignment_quota, num_iterations_per_assignment_quota, num_attempts_per_assignment_quota) 
VALUES (%s, %s, %s, %s, %s, %s, %s) 
ON DUPLICATE KEY UPDATE 
assignments_created_quota=VALUES(assignments_created_quota),
assignments_joined_quota=VALUES(assignments_joined_quota),
num_students_per_private_assignment_quota=VALUES(num_students_per_private_assignment_quota),
num_questions_per_assignment_quota=VALUES(num_questions_per_assignment_quota),
num_iterations_per_assignment_quota=VALUES(num_iterations_per_assignment_quota),
num_attempts_per_assignment_quota=VALUES(num_attempts_per_assignment_quota);"""
    params = [username, assignments_created_quota, assignments_joined_quota, num_students_per_private_assignment_quota, num_questions_per_assignment_quota, num_iterations_per_assignment_quota, num_attempts_per_assignment_quota]
    rds_cursor.execute(sql_query, params)
    rds_cursor.close()
    rds_connection.commit()
    rds_connection.close()

    return {"username": username,
            "assignments_created_quota": assignments_created_quota,
            "assignments_joined_quota": assignments_joined_quota,
            "num_students_per_private_assignment_quota": num_students_per_private_assignment_quota,
            "num_questions_per_assignment_quota": num_questions_per_assignment_quota,
            "num_iterations_per_assignment_quota": num_iterations_per_assignment_quota,
            "num_attempts_per_assignment_quota": num_attempts_per_assignment_quota,}

############################### DELETE RECORDS/TABLES ###############################

# drop student progress
def delete_quotas(username: str,):
  rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
  rds_cursor = rds_connection.cursor()
  sql_query = "DELETE FROM quotas WHERE username=%s;"
  params = [username,]
  rds_cursor.execute(sql_query, params)
  rds_cursor.close()
  rds_connection.commit()
  rds_connection.close()
  print("DELETED '{}' FROM QUOTAS TABLE.".format(username))

#####################################################################################

def get_table(filepath: str = "quotas.csv"):

    try:

        rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM quotas ORDER BY last_updated ASC;"""
        rds_cursor.execute(sql_query)
        records = rds_cursor.fetchall()

        with open(filepath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([desc[0] for desc in rds_cursor.description])  # Write header row
            csv_writer.writerows(records)

        rds_cursor.close()
        rds_connection.close()

    except:
        pass

def main():

    parser = argparse.ArgumentParser(description="Quotas Management Script")
    parser.add_argument("--get_table", action="store_true", help="Write the contents of the `quotas` table to quotas.csv.")
    args = parser.parse_args()
    
    if args.get_table:

        get_table()

    else:

        print("-"*150)
    
        for rds_table_name in ['quotas']:
            user_response = input("DELETE '{}' TABLE FROM RDS DATABASE? (yes/no): ".format(rds_table_name))
            if user_response == 'yes':
                rds_management.drop_table(rds_table_name=rds_table_name)
            elif user_response == 'no':
                print("NO ACTION TO '{}' TABLE.".format(rds_table_name))
            else:
                print("INVALID RESPONSE RECEIEVED. NO ACTION TO '{}' TABLE.".format(rds_table_name))
            print("-  "*50)

        create_quotas_table()

if __name__ == "__main__":
    
    main()