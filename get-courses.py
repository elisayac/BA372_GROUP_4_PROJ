import requests
import json

# OSU course catalog URL
url = "https://classes.oregonstate.edu/api/?page=fose&route=search"

# Source for course codes
cob_course_codes = {'BA', 'ACTG', 'BANA', 'BIS', 'DSGN', 'FIN', 'HM', 'MRKT', 'MGMT', 'SCLM'}

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


    

    
