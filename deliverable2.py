import sys
from ldap3 import Server, Connection, ALL, SUBTREE 
import json
import requests 
import re

def year_term_code():
    valid_terms = {'01', '02', '03', '04'}
    # Loop until valid inputs are provided
    while True:
        year_input = input("Enter the academic year (e.g., 2024 for the 2023-2024 academic year): ")
        if year_input.isdigit() and len(year_input) == 4:
            break
        print("Invalid year. Please enter a 4-digit year.")

    while True:
        term_input = input("Enter the term (01 for Fall, 02 for Winter, 03 for Spring, 04 for Summer): ").strip()
        if term_input in valid_terms:
            break
        print("Invalid term. Please enter '01', '02', '03', or '04'.")

    return year_input, term_input
  
#script 1
def get_courses():
    # OSU course catalog URL
    url = "https://classes.oregonstate.edu/api/?page=fose&route=search"

# Source for course codes
    cob_course_codes = {'BA', 'ACTG', 'BANA', 'BIS', 'DSGN', 'FIN', 'HM', 'MRKT', 'MGMT', 'SCLM'}

    # store user input for term and year here 
    year, term = year_term_code()

    # Form the srcdb string according to the values provided by user
    srcdb = f"{year}{term}"

    # Initialize a list to store selected fields of all courses
    selected_courses = []

    # Set up the query
    for course_code in cob_course_codes:
        query_dict = {
            "other": {"srcdb": srcdb},
            "criteria": [{"field": "subject", "value": course_code}]
        }

        # Convert query_dict into string
        query_str = json.dumps(query_dict)

        #show each course code query in terminal, print an error if the connection to API is failed
        try:
            response = requests.post(url, data=query_str, timeout=10)
            response.raise_for_status()  #Check if the request was successful
            print(f"\nQueried {course_code} for term {srcdb}, Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error... API call failed: {e}")
            continue

        #format the query results into json, if the results cannot be formatted into json, raise an error
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            print("Could not parse response into JSON")
            continue

        #if the key 'results' exists in response_json, show that results were found and how many courses there are for each course_code given the custom srcdb
        if 'results' in response_json:
            print(f"Results found for {course_code} in term {srcdb}: {len(response_json['results'])} courses")
        else:
            print(f"No results found for {course_code} in term {srcdb}")

        #pull the data or 'results' for each course that is found in API for the term and year
        for course in response_json.get('results', []):
            # Check if the course is cancelled
            if not course.get('iscancelled'):
                # Select only the desired fields and add them to the selected_courses list
                selected_course_info = {
                    "Course ID": f"{course.get('code')}_{course.get('crn')}",
                    "key": course.get('key'),
                    "code": course.get('code'),
                    "title": course.get('title'),
                    "crn": course.get('crn'),
                    "no": course.get('no'),
                    "instr": course.get('instr'),
                    "total": course.get('total')
                }
                selected_courses.append(selected_course_info)

    #Print the selected course information in comprehensive format 
    for course_info in selected_courses:
        print(json.dumps(course_info, indent=4))
    return srcdb, selected_courses

#script 2
def get_instructors(srcdb, selected_courses):
    for course_info in selected_courses:
        query_dict = {"srcdb": srcdb, "key" : ("crn:" + course_info["crn"])} #add course CRN (can be extracted with the previous program)

        #Convert query_dict into string
        query_str = json.dumps(query_dict)
        #print("query_str: ", query_str)

        url = "https://classes.oregonstate.edu/api/?page=fose&route=details"
        try:
            #Make POST request; pass query_str as data
            response = requests.post(url, data=query_str, timeout=10)
        except:
            print("Error... API call failed")
            exit(1)

        #added html stripping lines from reitsma in class 
        json_data= json.loads(response.text)
        instr_name = re.sub('<[^>]*>', ' ', json_data["instructordetail_html"])
        # split into first/last
        name_parts = instr_name.split()
        #just for debug
        if len(name_parts) <1: # handles empty instructor field
            #print(json.dumps(course_info, indent=4))
            #print( instr_name)
            #print (json.loads(response.text))
            course_info['first_name']= "NO INSTRUCTOR"
            course_info['last_name']= "NO INSTRUCTOR"
        else:
            course_info['first_name']= name_parts[0]
            course_info['last_name']= name_parts[1]
        #print(course_info['first_name'])


        #add first and last to dictionary
        #print(response.status_code)
        #print(response.text)
        #print(instr_name)
    return selected_courses

#breakout of ldap connection for getting emails
def connect_ldap(credentials_file):
    
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
    print("Connected to ldap")
    connect = Connection(server, user = 'onid\\' + ldap_login, password = ldap_password)

    #Bind
    if not connect.bind():
        print('error in bind', connect.result)
        exit(1)
    return connect


#script 3
#should pass in desired firstname, lastname, and open ldap connection
def get_email(first_name, last_name, connect):


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
        #print(email)
    else:
        email = "Nothing"
    return email

if (len(sys.argv) != 2):
  print("Program incorrectly started...")
  print("deliverable.py <credentials_file> ")
  exit(1)
srcdb, courses = get_courses()

courses = get_instructors(srcdb, courses)

connection=connect_ldap(sys.argv[1])

for course in courses:
    course['email'] = get_email(course['first_name'], course['last_name'], connection)
    print(course['email'])
        
#debug print use to test 
# print ("connected") 
# email_test= get_email("Gary", "Micheau", connection)
# email_test= get_email("Reindert", "Reitsma", connection)
# email_test= get_email("Joe", "Beaver", connection)
# print(email_test)
