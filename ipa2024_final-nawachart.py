#######################################################################################
# Yourname: Nawachart Ongcharoen
# Your student ID: 66070100
# Your GitHub Repo: https://github.com/IT2166070100/IPA2024-Final

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
import restconf_final as restconf
# import netmiko_final as netmiko
import ansible_final as ansible
from requests_toolbelt.multipart.encoder import MultipartEncoder
from dotenv import load_dotenv

load_dotenv()
#######################################################################################
# 2. Assign the Webex access token to the variable ACCESS_TOKEN using environment variables.

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId

roomIdToGetMessages = os.environ.get("WEBEX_ROOM_ID")


selected_method = None
selected_ip = None

while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}
    getHTTPHeader = {"Authorization": 'Bearer {}'.format(ACCESS_TOKEN)}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    json_data = r.json()

    # check if there are any messages in the "items" array
    if len(json_data["items"]) == 0:
        raise Exception("There are no messages in the room.")

    # store the array of messages
    messages = json_data["items"]
    
    # store the text of the first message in the array
    message = messages[0]["text"]
    print("Received message: " + message)


    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"

    if message.startswith("/66070100 "):
        # Remove the prefix and split the rest
        parts = message[len("/66070100 "):].strip().split()
        responseMessage = None
        command = None  # Initialize command

        if not selected_method:
            if len(parts) == 1 and parts[0].lower() in ["restconf", "netconf"]:
                selected_method = parts[0].lower()
                responseMessage = f"Ok: {selected_method.capitalize()}"
            elif len(parts) == 2:
                # Assume restconf
                selected_method = "restconf"
                ip_candidate = parts[0]
                command = parts[1].lower()
                if ip_candidate.count(".") != 3:
                    responseMessage = "Error: Invalid IP format"
                elif command not in ["create", "delete", "enable", "disable", "status", "gigabit_status", "showrun"]:
                    responseMessage = "Error: No command found."
                else:
                    selected_ip = ip_candidate
                    if command == "create":
                        responseMessage = restconf.create()
                    elif command == "delete":
                        responseMessage = restconf.delete()
                    elif command == "enable":
                        responseMessage = restconf.enable()
                    elif command == "disable":
                        responseMessage = restconf.disable()
                    elif command == "status":
                        responseMessage = restconf.status()
                    elif command == "gigabit_status":
                        responseMessage = "Netconf not implemented yet"
                    elif command == "showrun":
                        responseMessage = ansible.showrun()
            else:
                responseMessage = "Error: No method specified"
        else:
            # Method selected
            if len(parts) == 1:
                if parts[0].lower() in ["restconf", "netconf"]:
                    selected_method = parts[0].lower()
                    responseMessage = f"Ok: {selected_method.capitalize()}"
                elif parts[0] in ["create", "delete", "enable", "disable", "status", "gigabit_status", "showrun"]:
                    responseMessage = "Error: No IP specified"
                else:
                    responseMessage = "Error: No command found."
            elif len(parts) == 2:
                ip_candidate = parts[0]
                command = parts[1].lower()
                if ip_candidate.count(".") != 3:
                    responseMessage = "Error: Invalid IP format"
                elif command not in ["create", "delete", "enable", "disable", "status", "gigabit_status", "showrun"]:
                    responseMessage = "Error: No command found."
                else:
                    # Valid IP and command
                    selected_ip = ip_candidate
                    if command == "create":
                        responseMessage = restconf.create()
                    elif command == "delete":
                        responseMessage = restconf.delete()
                    elif command == "enable":
                        responseMessage = restconf.enable()
                    elif command == "disable":
                        responseMessage = restconf.disable()
                    elif command == "status":
                        responseMessage = restconf.status()
                    elif command == "gigabit_status":
                        responseMessage = "Netconf not implemented yet"
                    elif command == "showrun":
                        responseMessage = ansible.showrun()
            else:
                responseMessage = "Error: Invalid message format"

# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail

        if command == "showrun" and isinstance(responseMessage, dict) and responseMessage.get("msg") == 'ok':
            local_filepath = "backups/show_run_66070100_IPA-Router2.txt"  #----------------------------------------------------------------------
            upload_filename = "show_run_66070100_IPA-Router2.txt"
            fileobject = open(local_filepath, "rb")
            filetype = "text/plain"    #----------------------------------------------------------------------
            postData = {
                "roomId": roomIdToGetMessages,
                "text": "show running config",
                "files": (upload_filename, fileobject, filetype),          #----------------------------------------------------------------------
            }
            postData = MultipartEncoder(postData)                   #----------------------------------------------------------------------
            HTTPHeaders = {
            "Authorization": 'Bearer {}'.format(ACCESS_TOKEN),
            "Content-Type": postData.content_type,                       #----------------------------------------------------------------------
            }
        # other commands only send text, or no attached file.
        else:
            msg_to_send = str(responseMessage)
            postData = {"roomId": roomIdToGetMessages, "text": msg_to_send} #----------------------------------------------------------------------
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
            HTTPHeaders = {"Authorization": 'Bearer {}'.format(ACCESS_TOKEN), "Content-Type": "application/json"}   #----------------------------------------------------------------------

        # Post the call to the Webex Teams message API.
        r = requests.post(
            "https://webexapis.com/v1/messages",                            #----------------------------------------------------------------------
            data=postData,                                                  #----------------------------------------------------------------------
            headers=HTTPHeaders,                                            #----------------------------------------------------------------------
        )
        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
            )