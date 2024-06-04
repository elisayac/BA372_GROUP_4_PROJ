#!!!Note: this service only works for the current academic term; change the program accordingly !!!
import requests
import json

#Set up the query
query_dict = {"srcdb": "202403", "key" : "crn:???"} #add course CRN (can be extracted with the previous program)

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


#print(response.status_code)
print(response.text)
print(instr_name)