import sys
from ldap3 import Server, Connection, ALL, SUBTREE
import json
import requests


if (len(sys.argv) != 2):
  print("Program incorrectly started...")
  print("deliverable.py <credentials_file> ")
  exit(1)
  
#script 1
def get_courses():
    return

#script 2
def get_instructors(year, term, crn):
    return


#script 3
def get_emails(firstname, lastname, credentialsfile):
    return


#code goes here
