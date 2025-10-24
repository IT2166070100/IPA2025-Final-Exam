import subprocess
import tempfile
import os

def showrun():
    # read https://www.datacamp.com/tutorial/python-subprocess to learn more about subprocess
    command = ['ansible-playbook', 'playbook.yaml', '-i', 'hosts']
    result = subprocess.run(command, capture_output=True, text=True)

    # Check the return code. 0 means success.
    if result.returncode == 0 and 'ok=2' in result.stdout:
        return {"status": "OK", "msg": "ok"}
    else:
        # Combine stdout and stderr for a complete error message
        error_message = f"Ansible failed!\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        return {"status": "FAIL", "msg": error_message}

def motd_set(router_ip, message):
    # Create temporary inventory file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(f"{router_ip} ansible_host={router_ip} ansible_user=admin ansible_password=cisco ansible_connection=network_cli ansible_network_os=ios\n")
        temp_inventory = f.name
    
    try:
        # Run ansible-playbook to set MOTD
        command = ['ansible-playbook', 'motd_playbook.yaml', '-i', temp_inventory, '--extra-vars', f'motd_message="{message}"']
        result = subprocess.run(command, capture_output=True, text=True)

        # Check the return code. 0 means success.
        if result.returncode == 0 and 'ok=1' in result.stdout:
            return "Ok: success"
        else:
            # Combine stdout and stderr for a complete error message
            error_message = f"Ansible failed!\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            return error_message
    finally:
        # Clean up temp file
        os.unlink(temp_inventory)

if __name__ == "__main__":
    showrun()