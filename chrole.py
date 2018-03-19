import requests
from requests.auth import HTTPBasicAuth
import json
import argparse
import getpass


parser = argparse.ArgumentParser(description='This program will change the role of a user in Ranger.')
parser.add_argument('-d','--domain',help='Ranger domain', required=True)
parser.add_argument('-p','--port',help='Ranger port', required=True)
parser.add_argument('-g','--gateway',help='Knox gateway to Ranger', required=False)
parser.add_argument('-u','--admin_user',help='Admin username', required=True)
args = parser.parse_args()
USERNAME = args.admin_user
PASSWORD = getpass.getpass()


# username input
name = raw_input('What username\'s role would you like to change?')

# user get url
if args.gateway == None:
    ranger_url = args.domain  + ":" +  args.port
else:
    ranger_url = args.domain  + ":" +  args.port + args.gateway


headers = {'Content-Type': 'application/json', 'Accept': 'application/json',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
           'X-XSRF-HEADER': 'valid'}
payload = {'name': name}

ranger_rest_api = "/service/xusers/users"
url = ranger_url + ranger_rest_api
# get request with Admin username and password
myResponse = requests.get(url, headers=headers, params=payload,
                          auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=True)

# debug
# print (myResponse.status_code)
# myResponse.json()

# For successful API call, response code will be 200 (OK)
if (myResponse.ok):
    # print myResponse.content
    # Loading the response data into a dict variable
    # json.loads takes in only binary or string variables so using content to fetch binary content
    # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
    response = json.loads(myResponse.content)
    count = 0
    print("==================================")
    for i in response["vXUsers"]:
        print i["id"]
        print i["name"]
        print "=================================="
        count = count + 1
    # print count
    print('The following ') + str(count) + (' results were found')


    def chosen_id():
        while True:  # repeat forever unless it reaches "break" or "return"

            idconfirm = raw_input("Please confirm which id you would like to change role?")
            idconfirmed = raw_input("Is " + str(idconfirm) + " correct y/n ?")
            if "y" in idconfirmed:
                print "y"
                ranger_rest_api = "/service/xusers/users/"
                url = ranger_url + ranger_rest_api
                idurl = (url + str(idconfirm))
                getResponse = requests.get(idurl, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=True)
                if (getResponse.ok):
                    ranger_secure_api = "/service/xusers/secure/users"
                    url = ranger_url + ranger_secure_api
                    geturl = (url + str(idconfirm))
                    # global userresponse
                    print getResponse.headers
                    print getResponse.content
                    userResponse = json.loads(getResponse.content)
                    if (userResponse["userRoleList"][0] == "ROLE_SYS_ADMIN"):
                        userrole = raw_input("User is an Admin role, would you like to change this role to user? y/n")
                        if (userrole == "y"):
                            userResponse["userRoleList"][0] = "ROLE_USER"
                            del userResponse["password"]
                            print(userResponse)
                            print("jsondump of altered response")
                            print (json.dumps(userResponse))
                            myPutResponse = requests.put(geturl, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD),
                                                         verify=True,
                                                         data=json.dumps(userResponse))
                            print(response)
                            print(myPutResponse.status_code)
                            print(myPutResponse.content)
                            print("user is now an USER role!")
                        else:
                            continue

                    else:
                        adminrole = raw_input(
                            "User is a User role, would you like to change this user to admin role? y/n")
                        if (adminrole == "y"):
                            userResponse["userRoleList"][0] = "ROLE_SYS_ADMIN"
                            del userResponse["password"]

                            myPutResponse = requests.put(geturl, headers=headers, auth=HTTPBasicAuth(USERNAME, PASSWORD),
                                                         verify=True, data=json.dumps(userResponse))
                            print(response)
                            print(myPutResponse.status_code)
                            print(myPutResponse.content)
                            print("user is now an Admin role!")
                        else:
                            continue

                else:
                    # If response code is not ok (200), print the resulting http error code with description
                    myResponse.raise_for_status()
                    exit()

            elif "n" in idconfirmed:
                continue
            else:
                print "sorry, you can only choose y or n"
                continue  # jumps back to the "while True:" line
            return  # finished; exit the function.


    chosen_id()

else:
    # If response code is not ok (200), print the resulting http error code with description
    myResponse.raise_for_status()
