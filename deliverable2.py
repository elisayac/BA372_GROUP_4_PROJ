import sys
from ldap3 import Server, Connection, ALL, SUBTREE
import json
import requests

def main():
  if (len(sys.argv) != 2):
  print("Program incorrectly started...")
  print("deliverable.py <credentials_file> ")
  exit(1)
#loop for script 2 based on script 1
for course, crn in courses.items():
    instructor, error = get_instructors(year, term, crn)
    if error:
        print(f"Error fetching instructor for {course}: {error}")
        continue
  
#script 1
def get_courses():
    return

#script 2
def get_instructors(year, term, crn):
    return


#script 3
def get_email(first_name, last_name, credentials_file):

    #if (len(sys.argv) != 4):
    # print("Program incorrectly started...")
    # print("ldap_query_for_onid.py <credentials_file> <first_name> <last_name>")
    # exit(1)

    # ldap_credentials_file = sys.argv[1]
    # first_name = sys.argv[2]
    # last_name = sys.argv[3]

    #Read LDAP credentials from credentials file
    try:
        fp = open(credentials_file, "r")
    except:
        print("Error... opening credentials file")
        exit(1)
    line_1 = fp.readline()
    line_2 = fp.readline()
    fp.close()

    ldap_login_list = line_1.split("=")
    ldap_login = ldap_login_list[1].rstrip()

    ldap_password_list = line_2.split("=")
    ldap_password = ldap_password_list[1].lstrip().rstrip()

    #Define the server
    server = Server('onid-k-dc01.onid.oregonstate.edu', get_info = ALL)

    #Define the connection
    connect = Connection(server, user = 'onid\\' + ldap_login, password = ldap_password)

    #Bind
    if not connect.bind():
        print('error in bind', connect.result)
        exit(1)

    #Set search parameters
    ldap_filter = "(&(sn=" + last_name + ")(givenName=" + first_name + "))"

    #Set attributes to return
    ldap_attributes = ["userPrincipalName"]

    #Search
    try:
        connect.search(search_base = 'DC=onid,DC=oregonstate,DC=edu',
                     search_filter = ldap_filter,
                     attributes = ldap_attributes,
                        search_scope = SUBTREE)
    except:
        print("Error... searching")
        exit(1)

    #Extract the email address from the response
    if len(connect.response) == 1:
        email = (connect.response[0]['attributes']['userPrincipalName'])
        print(email)
    else:
        email = "Nothing"
    return email


#code goes here
