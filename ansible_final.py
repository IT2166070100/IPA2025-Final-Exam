import subprocess
import tempfile
import os

def showrun(router_ip):
    # Create temporary inventory file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
        f.write(f"{router_ip} ansible_host={router_ip} ansible_user=admin ansible_password=cisco ansible_connection=network_cli ansible_network_os=ios\n")
        temp_inventory = f.name
    
    try:
        # Run ansible-playbook to get show run
        command = ['ansible-playbook', 'playbook.yaml', '-i', temp_inventory, '--extra-vars', f'router_ip={router_ip}']
        result = subprocess.run(command, capture_output=True, text=True)

        # Check the return code. 0 means success.
        if result.returncode == 0 and 'failed=0' in result.stdout:
            # Check if the file was actually created
            file_path = f"backups/show_run_66070100_{router_ip}.txt"
            if os.path.exists(file_path):
                return {"status": "OK", "msg": "ok"}
            else:
                return {"status": "FAIL", "msg": f"Ansible playbook succeeded but file {file_path} was not created."}
        else:
            # Combine stdout and stderr for a complete error message
            error_message = f"Ansible failed!\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            return {"status": "FAIL", "msg": error_message}
    finally:
        # Clean up temp file
        os.unlink(temp_inventory)

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