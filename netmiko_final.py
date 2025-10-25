from netmiko import ConnectHandler
from pprint import pprint

device_ip = "10.0.15.62"
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",
    "ip": device_ip,
    "username": username,
    "password": password,
}


def gigabit_status():
    ans = ""
    with ConnectHandler(**device_params) as ssh:
        up = 0
        down = 0
        admin_down = 0
        result = ssh.send_command("sh int", use_textfsm=True)
        for status in result:
            if status["interface"].startswith("GigabitEthernet"):
                ans += f"{status['interface']} {status['link_status']},"
                if status['link_status'] == "up":
                    up += 1
                elif status['link_staus'] == "down":
                    down += 1
                elif status['link_status'] == "administratively down":
                    admin_down += 1
        ans = f"{ans[:-1]} -> {up} up, {down} down, {admin_down} administratively down"
        pprint(ans)
        return ans


from netmiko import ConnectHandler


def gigabit_status(router_ip):
    device_params = {
        "device_type": "cisco_ios",
        "ip": router_ip,
        "username": "admin",
        "password": "cisco",
    }
    ans = ""
    with ConnectHandler(**device_params) as ssh:
        result = ssh.send_command("sh int", use_textfsm=True)
        up = 0
        down = 0
        admin_down = 0
        for status in result:
            if status["interface"].startswith("GigabitEthernet"):
                ans += f"{status['interface']} {status['link_status']},"
                if status["link_status"] == "up":
                    up += 1
                elif status["link_status"] == "down":
                    down += 1
                elif status["link_status"] == "administratively down":
                    admin_down += 1
        if ans:
            ans = f"{ans[:-1]} -> {up} up, {down} down, {admin_down} administratively down"
        else:
            ans = "No GigabitEthernet interfaces found"
        return ans


def motd_get(router_ip):
    valid_ips = ['10.0.15.61', '10.0.15.62', '10.0.15.63', '10.0.15.64', '10.0.15.65']
    if router_ip not in valid_ips:
        return "Error: No MOTD Configured"
    
    device_params = {
        "device_type": "cisco_ios",
        "ip": router_ip,
        "username": "admin",
        "password": "cisco",
    }
    with ConnectHandler(**device_params) as ssh:
        result = ssh.send_command("show banner motd")
        if result.strip() == "":
            return "Error: No MOTD Configured"
        else:
            return result.strip()