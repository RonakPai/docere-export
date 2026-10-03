'''
Functions for managing user permissions.
'''
import csv
import argparse

import keys
import rds_management

################################### CREATE TABLES ###################################

def create_permissions_table():
  
  rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
  rds_cursor = rds_connection.cursor()
  sql_query = '''CREATE TABLE IF NOT EXISTS permissions (
    username VARCHAR(255) NOT NULL,
    name TEXT NOT NULL,
    organization TEXT NOT NULL,
    subscription_tier TEXT NOT NULL,
    active BOOL NOT NULL,
    allow_hide_assignment_answer BOOL NOT NULL,
    allow_disable_assignment_restart BOOL NOT NULL,
    allow_private_assignment BOOL NOT NULL,
    enable_ai_generated_final_report BOOL NOT NULL,
    enable_regenerate_assignment_based_on_final_report BOOL NOT NULL,
    enable_ai_generated_assignment_simulation BOOL NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (username))'''
  rds_cursor.execute(sql_query)
  rds_cursor.close()
  rds_connection.commit()
  rds_connection.close()
  print("CREATED 'permissions' TABLE.")

#################################### READ TABLES ####################################

def get_user_basic_info(username: str,):

    output = {"username": username,
              "name": "",
              "organization": "",}
    
    try:
        rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM permissions WHERE username=%s;"""
        params = [username,]
        rds_cursor.execute(sql_query, params)
        record = rds_cursor.fetchone()
        rds_cursor.close()
        rds_connection.close()
        output["username"] = record[0]
        output["name"] = record[1]
        output["organization"] = record[2]
    except:
        pass
    
    return output

def get_permissions(username: str,):
   
    output = {"username": username,
              "name": "",
              "organization": "",
              "subscription_tier": "",
              "active": False,
              "allow_hide_assignment_answer": False,
              "allow_disable_assignment_restart": False,
              "allow_private_assignment": False,
              "enable_ai_generated_final_report": False,
              "enable_regenerate_assignment_based_on_final_report": False,
              "enable_ai_generated_assignment_simulation": False,}
    
    try:
        rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM permissions WHERE username=%s;"""
        params = [username,]
        rds_cursor.execute(sql_query, params)
        record = rds_cursor.fetchone()
        rds_cursor.close()
        rds_connection.close()
        output["username"] = record[0]
        output["name"] = record[1]
        output["organization"] = record[2]
        output["subscription_tier"] = record[3]
        output["active"] = record[4]
        output["allow_hide_assignment_answer"] = record[5]
        output["allow_disable_assignment_restart"] = record[6]
        output["allow_private_assignment"] = record[7]
        output["enable_ai_generated_final_report"] = record[8]
        output["enable_regenerate_assignment_based_on_final_report"] = record[9]
        output["enable_ai_generated_assignment_simulation"] = record[10]
    except:
        pass
    
    return output
    
################################### UPDATE TABLES ###################################

def update_name(username: str,
                name: str,):

    rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
    rds_cursor = rds_connection.cursor()
    sql_query = """UPDATE permissions
SET name=%s
WHERE username=%s;"""
    params = [name, username,]
    rds_cursor.execute(sql_query, params)
    rds_cursor.close()
    rds_connection.commit()
    rds_connection.close()

    return {"username": username,
            "name": name,}

def update_organization(username: str,
                        organization: str,):

    rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
    rds_cursor = rds_connection.cursor()
    sql_query = """UPDATE permissions
SET organization=%s
WHERE username=%s;"""
    params = [organization, username,]
    rds_cursor.execute(sql_query, params)
    rds_cursor.close()
    rds_connection.commit()
    rds_connection.close()

    return {"username": username,
            "organization": organization,}

# def set_beta_tester_permissions(username: str,
#                                 name: str,
#                                 organization: str,):
   
#    subscription_tier = "beta_tester"
#    active = True
#    allow_hide_assignment_answer = True
#    allow_disable_assignment_restart = True
#    allow_private_assignment = True
#    enable_ai_generated_final_report = True
#    enable_regenerate_assignment_based_on_final_report = True
#    enable_ai_generated_assignment_simulation = True

#    return set_permissions(username=username,
#                           name=name,
#                           organization=organization,
#                           subscription_tier=subscription_tier,
#                           active=active,
#                           allow_hide_assignment_answer=allow_hide_assignment_answer,
#                           allow_disable_assignment_restart=allow_disable_assignment_restart,
#                           allow_private_assignment=allow_private_assignment,
#                           enable_ai_generated_final_report=enable_ai_generated_final_report,
#                           enable_regenerate_assignment_based_on_final_report=enable_regenerate_assignment_based_on_final_report,
#                           enable_ai_generated_assignment_simulation=enable_ai_generated_assignment_simulation)
    
def set_free_tier_permissions(username: str,
                              name: str,
                              organization: str,):
   
   subscription_tier = "free"
   active = True
   allow_hide_assignment_answer = False
   allow_disable_assignment_restart = False # unused feature
   allow_private_assignment = False
   enable_ai_generated_final_report = True
   enable_regenerate_assignment_based_on_final_report = True
   enable_ai_generated_assignment_simulation = False

   return set_permissions(username=username,
                          name=name,
                          organization=organization,
                          subscription_tier=subscription_tier,
                          active=active,
                          allow_hide_assignment_answer=allow_hide_assignment_answer,
                          allow_disable_assignment_restart=allow_disable_assignment_restart,
                          allow_private_assignment=allow_private_assignment,
                          enable_ai_generated_final_report=enable_ai_generated_final_report,
                          enable_regenerate_assignment_based_on_final_report=enable_regenerate_assignment_based_on_final_report,
                          enable_ai_generated_assignment_simulation=enable_ai_generated_assignment_simulation)

def set_student_tier_permissions(username: str,
                                 name: str,
                                 organization: str,):
   
   subscription_tier = "student"
   active = True
   allow_hide_assignment_answer = False
   allow_disable_assignment_restart = False # unused feature
   allow_private_assignment = True
   enable_ai_generated_final_report = True
   enable_regenerate_assignment_based_on_final_report = True
   enable_ai_generated_assignment_simulation = False

   return set_permissions(username=username,
                          name=name,
                          organization=organization,
                          subscription_tier=subscription_tier,
                          active=active,
                          allow_hide_assignment_answer=allow_hide_assignment_answer,
                          allow_disable_assignment_restart=allow_disable_assignment_restart,
                          allow_private_assignment=allow_private_assignment,
                          enable_ai_generated_final_report=enable_ai_generated_final_report,
                          enable_regenerate_assignment_based_on_final_report=enable_regenerate_assignment_based_on_final_report,
                          enable_ai_generated_assignment_simulation=enable_ai_generated_assignment_simulation)

def set_teacher_tier_permissions(username: str,
                                 name: str,
                                 organization: str,):
   
   subscription_tier = "teacher"
   active = True
   allow_hide_assignment_answer = True
   allow_disable_assignment_restart = False # unused feature
   allow_private_assignment = True
   enable_ai_generated_final_report = True
   enable_regenerate_assignment_based_on_final_report = True
   enable_ai_generated_assignment_simulation = True

   return set_permissions(username=username,
                          name=name,
                          organization=organization,
                          subscription_tier=subscription_tier,
                          active=active,
                          allow_hide_assignment_answer=allow_hide_assignment_answer,
                          allow_disable_assignment_restart=allow_disable_assignment_restart,
                          allow_private_assignment=allow_private_assignment,
                          enable_ai_generated_final_report=enable_ai_generated_final_report,
                          enable_regenerate_assignment_based_on_final_report=enable_regenerate_assignment_based_on_final_report,
                          enable_ai_generated_assignment_simulation=enable_ai_generated_assignment_simulation)

def set_school_tier_permissions(username: str,
                                name: str,
                                organization: str,):
   
   subscription_tier = "school"
   active = True
   allow_hide_assignment_answer = True
   allow_disable_assignment_restart = False # unused feature
   allow_private_assignment = True
   enable_ai_generated_final_report = True
   enable_regenerate_assignment_based_on_final_report = True
   enable_ai_generated_assignment_simulation = True

   return set_permissions(username=username,
                          name=name,
                          organization=organization,
                          subscription_tier=subscription_tier,
                          active=active,
                          allow_hide_assignment_answer=allow_hide_assignment_answer,
                          allow_disable_assignment_restart=allow_disable_assignment_restart,
                          allow_private_assignment=allow_private_assignment,
                          enable_ai_generated_final_report=enable_ai_generated_final_report,
                          enable_regenerate_assignment_based_on_final_report=enable_regenerate_assignment_based_on_final_report,
                          enable_ai_generated_assignment_simulation=enable_ai_generated_assignment_simulation)

def set_permissions(username: str,
                    name: str,
                    organization: str,
                    subscription_tier: str,
                    active: bool,
                    allow_hide_assignment_answer: bool,
                    allow_disable_assignment_restart: bool,
                    allow_private_assignment: bool,
                    enable_ai_generated_final_report: bool,
                    enable_regenerate_assignment_based_on_final_report: bool,
                    enable_ai_generated_assignment_simulation: bool):
    
    rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
    rds_cursor = rds_connection.cursor()
    sql_query = """INSERT INTO permissions (username, name, organization, subscription_tier, active, allow_hide_assignment_answer, allow_disable_assignment_restart, allow_private_assignment, enable_ai_generated_final_report, enable_regenerate_assignment_based_on_final_report, enable_ai_generated_assignment_simulation) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
ON DUPLICATE KEY UPDATE 
name=VALUES(name),
organization=VALUES(organization),
subscription_tier=VALUES(subscription_tier),
active=VALUES(active),
allow_hide_assignment_answer=VALUES(allow_hide_assignment_answer),
allow_disable_assignment_restart=VALUES(allow_disable_assignment_restart),
allow_private_assignment=VALUES(allow_private_assignment),
enable_ai_generated_final_report=VALUES(enable_ai_generated_final_report),
enable_regenerate_assignment_based_on_final_report=VALUES(enable_regenerate_assignment_based_on_final_report),
enable_ai_generated_assignment_simulation=VALUES(enable_ai_generated_assignment_simulation);"""
    params = [username, name, organization, subscription_tier, active, allow_hide_assignment_answer, allow_disable_assignment_restart, allow_private_assignment, enable_ai_generated_final_report, enable_regenerate_assignment_based_on_final_report, enable_ai_generated_assignment_simulation]
    rds_cursor.execute(sql_query, params)
    rds_cursor.close()
    rds_connection.commit()
    rds_connection.close()

    return {"username": username,
            "name": name,
            "organization": organization,
            "subscription_tier": subscription_tier,
            "active": active,
            "allow_hide_assignment_answer": allow_hide_assignment_answer,
            "allow_disable_assignment_restart": allow_disable_assignment_restart,
            "allow_private_assignment": allow_private_assignment,
            "enable_ai_generated_final_report": enable_ai_generated_final_report,
            "enable_regenerate_assignment_based_on_final_report": enable_regenerate_assignment_based_on_final_report,
            "enable_ai_generated_assignment_simulation": enable_ai_generated_assignment_simulation}

############################### DELETE RECORDS/TABLES ###############################

# drop user permissions
def delete_permissions(username: str,):
    current_permissions = get_permissions(username=username)
    _ = set_permissions(username=username, 
                        name=current_permissions['name'],
                        organization=current_permissions['organization'],
                        subscription_tier=current_permissions['subscription_tier'],
                        active=False,
                        allow_hide_assignment_answer=False,
                        allow_disable_assignment_restart=False,
                        allow_private_assignment=False,
                        enable_ai_generated_final_report=False,
                        enable_regenerate_assignment_based_on_final_report=False,
                        enable_ai_generated_assignment_simulation=False)
    print("UPDATED '{}' PERMISSIONS TO 'offboarded'.".format(username))

#####################################################################################

def get_table(filepath: str = "permissions.csv"):

    try:

        rds_connection = rds_management.create_connection(keys.AWS_RDS_ENDPOINT, keys.AWS_RDS_USERNAME, keys.AWS_RDS_PASSWORD, keys.AWS_RDS_MVP_DATABASE_NAME)
        rds_cursor = rds_connection.cursor()
        sql_query = """SELECT * FROM permissions ORDER BY last_updated ASC;"""
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

    parser = argparse.ArgumentParser(description="Permissions Management Script")
    parser.add_argument("--get_table", action="store_true", help="Write the contents of the `permissions` table to permissions.csv.")
    args = parser.parse_args()
    
    if args.get_table:

        get_table()

    else:

        print("-"*150)
        
        for rds_table_name in ['permissions']:
            user_response = input("DELETE '{}' TABLE FROM RDS DATABASE? (yes/no): ".format(rds_table_name))
            if user_response == 'yes':
                rds_management.drop_table(rds_table_name=rds_table_name)
            elif user_response == 'no':
                print("NO ACTION TO '{}' TABLE.".format(rds_table_name))
            else:
                print("INVALID RESPONSE RECEIEVED. NO ACTION TO '{}' TABLE.".format(rds_table_name))
            print("-  "*50)

        create_permissions_table()

if __name__ == "__main__":
    
    main()