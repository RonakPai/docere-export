'''
Run this file after updating `valid_user_substrings.csv`
to update the beta tester list.
'''

import csv

import keys
import rds_management

################################## TABLE MANAGEMENT #################################

def create_beta_testers_table():
    
    rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
    rds_cursor = rds_connection.cursor()
    sql_query = '''CREATE TABLE IF NOT EXISTS beta_testers (
        valid_user_substring VARCHAR(255) NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (valid_user_substring))'''
    rds_cursor.execute(sql_query)
    rds_cursor.close()
    rds_connection.commit()
    rds_connection.close()
    print("CREATED 'beta_testers' TABLE.")

def drop_beta_testers_table():
    rds_management.drop_table(rds_table_name="beta_testers")

def populate_beta_testers_table():

    valid_user_substring_list = []
    with open('valid_beta_tester_substrings.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            valid_user_substring_list.append(row[0].strip())
    
    rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
    rds_cursor = rds_connection.cursor()
    sql_query = """INSERT INTO beta_testers (valid_user_substring) VALUES (%s)"""
    params = [(s,) for s in valid_user_substring_list]
    rds_cursor.executemany(sql_query, params)
    rds_cursor.close()
    rds_connection.commit()
    rds_connection.close()
    print("POPULATED 'beta_testers' TABLE.")

#####################################################################################

################################## USER VALIDATION ##################################

def validate_user(username: str):

    valid = False

    rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
    rds_cursor = rds_connection.cursor()
    sql_query = """SELECT valid_user_substring FROM beta_testers"""
    rds_cursor.execute(sql_query)
    valid_user_substrings = [record[0].lower() for record in rds_cursor.fetchall()]
    rds_cursor.close()
    rds_connection.close()

    username = username.lower()
    for valid_user_substring in valid_user_substrings:
        if valid_user_substring in username:
            valid = True
    
    return valid

#####################################################################################

######################################## MAIN #######################################

def main():

    drop_beta_testers_table()
    create_beta_testers_table()
    populate_beta_testers_table()

if __name__ == "__main__":
    main()

#####################################################################################