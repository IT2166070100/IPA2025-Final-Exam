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

selected_method = None

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
        # extract the command
        command = message.split("/66070100 ")[1].split(" ")[0].lower().strip()
        print(command)

        # Check for method selection first
        if command == "restconf":
            selected_method = "restconf"
            responseMessage = "Ok: Restconf"
        elif command == "netconf":
            selected_method = "netconf"
            responseMessage = "Ok: Netconf"
        # Only allow config commands if method is set
        elif command in ["create", "delete", "enable", "disable", "status", "gigabit_status", "showrun"]:
            if not selected_method:
                responseMessage = "Error: No method specified"
            else:
                if selected_method == "restconf":
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
                    else:
                        responseMessage = "Error: No command found."
                elif selected_method == "netconf":
                    # TOBE ADDED NETCONF ------------------------------------------------------------------------------------------------
                    responseMessage = "Ok: Netconf"
                # For gigabit_status and showrun
                if command == "gigabit_status":
                    responseMessage = netmiko.gigabit_status()
                elif command == "showrun":
                    responseMessage = ansible.showrun()
        else:
            responseMessage = "Error: No command found."

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

        if command == "showrun" and responseMessage.get("msg") == 'ok':
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