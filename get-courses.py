#!!!Note: this service only works for the current academic term; change the program accordingly !!!
import requests
import json

#OSU course catalog URL
url = "https://classes.oregonstate.edu/api/?page=fose&route=search"

#https://catalog.oregonstate.edu/college-departments/business/#coursestext SOURCE for couse codes
cob_couse_codes= {'BA', 'ACTG', 'BANA','BIS', 'DSGN', 'FIN', 'HM', 'MRKT', 'MGMT','SCLM'}

##Nicks code start
def year_term_code():
    valid_terms = {'01', '02', '03', '04'}
    #Loop until valid inputs are provided
    while True:
        year_input = input("Enter the academic year (e.g., 2024 for the 2023-2024 academic year): ")
        #make sure we only accept years, numeric only, must be 4 digits long
        if year_input.isdigit() and len(year_input) == 4:
            break
        print("Invalid year. Please enter a 4-digit year.")

    #Get the term
    while True:
        term_input = input("Enter the term (01 for Fall, 02 for Winter, 03 for Spring, 04 for Summer): ").strip()
        if term_input in valid_terms:
            break
        print("Invalid term. Please enter '01', '02', '03', or '04'.")

    return year_input, term_input
    
#Get user input for term and year
year, term = year_term_code()

#Form the srcdb string according to the values provided by user
srcdb = f"{year}{term}"

#Initialize a dictionary to store all courses
all_courses = {}
##Nicks code end    

#Set up the query
for course_code in cob_couse_codes:
    
    query_dict = {
        #replaced static 202403 string with dynamic user text entry (srcdb)
    "other" : {"srcdb": srcdb},  #Now uses the user inputted values, not just 202403
    "criteria" : [ {"field" : "subject", "value" : course_code } ] 
    }

    #Convert query_dict into string
    query_str = json.dumps(query_dict)

    #print("query_str: ", query_str)
    try:
    #Make POST request; pass query_str as data
        response = requests.post(url, data=query_str, timeout=10)
    except:
        print("Error... API call failed")
        exit(1)

    #print(response.status_code)
    print(response.text)#todo parse output as JSON and store each course in the same dictionary
    

    
