#Python program which retrieves ONID email from LDAP using user's first and last
#name.
#
#Since the program requires ONID username and password to connect to ONID LDAP,
#username and password must be stored in a file using the following format:
#
#user=onid_user_id
#password=onid_password
#
#Instead of hardwiring these credentials in the program, we store them in a (credentials) file and 
#pass the file to the program on the command-line.
#
#In this version of the program, the first and last name of the ONID user whose
#email we want are also passed on the command line.
#
#Example: if the credentials file is 'z:\credentials.txt' and we are looking for
#the email of Logan Steele, we call the program on the command-line as follows:
#
#python ldap_query_for_onid.py z:\credentials.txt Logan Steele

import sys
from 
import Server, Connection, ALL, SUBTREE # type: ignore

if (len(sys.argv) != 4):
  print("Program incorrectly started...")
  print("ldap_query_for_onid.py <credentials_file> <first_name> <last_name>")
  exit(1)

ldap_credentials_file = sys.argv[1]
first_name = sys.argv[2]
last_name = sys.argv[3]

#Read LDAP credentials from credentials file
try:
  fp = open(ldap_credentials_file, "r")
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
  print("Nothing")
