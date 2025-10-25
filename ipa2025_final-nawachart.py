#######################################################################################
# Yourname: Nawachart Ongcharoen
# Your student ID: 66070100
# Your GitHub Repo: https://github.com/IT2166070100/IPA2025-Final-Exam

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
import restconf_final as restconf
import netconf_final as netconf
import netmiko_final as netmiko
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

# For storing selected method and IP
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
    if len(messages) > 0 and "text" in messages[0]:
        message = messages[0]["text"]
        print("Received message: " + message)
    else:
        continue  # Skip this iteration if no valid text message


    # check if the text of the message starts with the magic character "/" followed by your studentID and a space and followed by a command name
    #  e.g.  "/66070123 create"

    if message.startswith("/66070100 "):
        # Remove the prefix and split the rest
        rest = message[len("/66070100 "):].strip()
        parts = rest.split(' ', 2)  # Split into at most 3 parts: ip, command, message
        responseMessage = None
        command = None  # Initialize command

        # Handle commands that don't require method selection first
        if len(parts) == 2:
            ip_candidate = parts[0]
            command = parts[1].lower()
            if ip_candidate.count(".") == 3 and command in ["gigabit_status", "showrun", "motd"]:
                if command == "gigabit_status":
                    responseMessage = netmiko.gigabit_status(ip_candidate)
                elif command == "showrun":
                    responseMessage = ansible.showrun(ip_candidate)
                elif command == "motd":
                    responseMessage = netmiko.motd_get(ip_candidate)
            else:
                # Fall back to method-based logic
                pass  # Will be handled below
        elif len(parts) == 3:
            ip_candidate = parts[0]
            command = parts[1].lower()
            motd_message = parts[2]
            if command == "motd" and ip_candidate.count(".") == 3:
                responseMessage = ansible.motd_set(ip_candidate, motd_message)
            else:
                pass  # Fall back

        if responseMessage is None:
            # Method-based commands
            if not selected_method:
                if len(parts) == 1 and parts[0].lower() in ["restconf", "netconf"]:
                    selected_method = parts[0].lower()
                    responseMessage = f"Ok: {selected_method.capitalize()}"
                else:
                    responseMessage = "Error: No method specified"
            else:
                # Method selected
                if len(parts) == 1:
                    if parts[0].lower() in ["restconf", "netconf"]:
                        selected_method = parts[0].lower()
                        responseMessage = f"Ok: {selected_method.capitalize()}"
                    elif parts[0] in ["create", "delete", "enable", "disable", "status"]:
                        responseMessage = "Error: No IP specified"
                    else:
                        responseMessage = "Error: No command found."
                elif len(parts) == 2:
                    ip_candidate = parts[0]
                    command = parts[1].lower()
                    if ip_candidate.count(".") != 3:
                        responseMessage = "Error: Invalid IP format"
                    elif command not in ["create", "delete", "enable", "disable", "status"]:
                        responseMessage = "Error: No command found."
                    else:
                        # Valid IP and command
                        if command == "create":
                            if selected_method == "restconf":
                                responseMessage = restconf.create(ip_candidate)
                            else:
                                responseMessage = netconf.create(ip_candidate)
                        elif command == "delete":
                            if selected_method == "restconf":
                                responseMessage = restconf.delete(ip_candidate)
                            else:
                                responseMessage = netconf.delete(ip_candidate)
                        elif command == "enable":
                            if selected_method == "restconf":
                                responseMessage = restconf.enable(ip_candidate)
                            else:
                                responseMessage = netconf.enable(ip_candidate)
                        elif command == "disable":
                            if selected_method == "restconf":
                                responseMessage = restconf.disable(ip_candidate)
                            else:
                                responseMessage = netconf.disable(ip_candidate)
                        elif command == "status":
                            if selected_method == "restconf":
                                responseMessage = restconf.status(ip_candidate)
                            else:
                                responseMessage = netconf.status(ip_candidate)
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
            local_filepath = f"backups/show_run_66070100_{ip_candidate}.txt"  
            upload_filename = f"show_run_66070100_{ip_candidate}.txt"
            fileobject = open(local_filepath, "rb")
            filetype = "text/plain"    
            postData = {
                "roomId": roomIdToGetMessages,
                "text": f"show running config for {ip_candidate}",
                "files": (upload_filename, fileobject, filetype),          
            }
            postData = MultipartEncoder(postData)                   
            HTTPHeaders = {
            "Authorization": 'Bearer {}'.format(ACCESS_TOKEN),
            "Content-Type": postData.content_type,                       
            }
        # other commands only send text, or no attached file.
        else:
            msg_to_send = str(responseMessage)
            postData = {"roomId": roomIdToGetMessages, "text": msg_to_send} 
            postData = json.dumps(postData)

            # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
            HTTPHeaders = {"Authorization": 'Bearer {}'.format(ACCESS_TOKEN), "Content-Type": "application/json"}   

        # Post the call to the Webex Teams message API.
        r = requests.post(
            "https://webexapis.com/v1/messages",                            
            data=postData,                                                  
            headers=HTTPHeaders,                                            
        )
        if not r.status_code == 200:
            raise Exception(
                "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
            )