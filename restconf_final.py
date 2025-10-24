import json
import requests
requests.packages.urllib3.disable_warnings()

# Router IP Address is 10.0.15.181-184
# api_url = "https://10.0.15.62/restconf/data"

studentID = "66070100"

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}  #--------------------------------------------------------------------------------------
basicauth = ("admin", "cisco")


def create(router_ip):
    api_url = f"https://{router_ip}/restconf/data"
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{studentID}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [{"ip": "172.1.0.1", "netmask": "255.255.255.0"}]
            },
            "ietf-ip:ipv6": {},
        }
    }

    resp = requests.put(
        f"{api_url}/ietf-interfaces:interfaces/interface=Loopback{studentID}", 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if(resp.status_code == 201):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {studentID} is created successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot create: Interface loopback {studentID}"



def delete(router_ip):
    api_url = f"https://{router_ip}/restconf/data"
    resp = requests.delete(
        f"{api_url}/ietf-interfaces:interfaces/interface=Loopback{studentID}", 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {studentID} is deleted successfully using Restconf"
    else:
        print(f'Cannot delete: Interface loopback {studentID}')
        return f'Cannot delete: Interface loopback {studentID}'


def enable(router_ip):
    api_url = f"https://{router_ip}/restconf/data"
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": "Loopback{}".format(studentID),
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
        }
    }

    resp = requests.patch(
        f"{api_url}/ietf-interfaces:interfaces/interface=Loopback{studentID}", 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {studentID} is enabled successfully using Restconf"
    else:
        print(f'Cannot enable: Interface loopback {studentID}')
        return f'Cannot enable: Interface loopback {studentID}'


def disable(router_ip):
    api_url = f"https://{router_ip}/restconf/data"
    yangConfig = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{studentID}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": False,
        }
    }

    resp = requests.patch(
        f"{api_url}/ietf-interfaces:interfaces/interface=Loopback{studentID}", 
        data=json.dumps(yangConfig), 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        return f"Interface loopback {studentID} is shutdowned successfully using Restconf"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Cannot shutdown: Interface loopback {studentID}"


def status(router_ip):
    api_url = f"https://{router_ip}/restconf/data"
    resp = requests.get(
        f"{api_url}/ietf-interfaces:interfaces-state/interface=Loopback{studentID}", 
        auth=basicauth, 
        headers=headers, 
        verify=False
        )

    if(resp.status_code >= 200 and resp.status_code <= 299):
        print("STATUS OK: {}".format(resp.status_code))
        response_json = resp.json()
        admin_status = response_json["ietf-interfaces:interface"]["admin-status"] #-----------------------------------
        oper_status = response_json["ietf-interfaces:interface"]["oper-status"]  #-----------------------------------
        if admin_status == 'up' and oper_status == 'up':
            return f"Interface loopback {studentID} is enabled (checked by Restconf)"
        elif admin_status == 'down' and oper_status == 'down':
            return f"Interface loopback {studentID} is disabled (checked by Restconf)"
    elif(resp.status_code == 404):
        print("STATUS NOT FOUND: {}".format(resp.status_code))
        return f"No Interface loopback {studentID} (checked by Restconf)"
    else:
        print('Error. Status Code: {}'.format(resp.status_code))
        return f"Undefined Error5"
        