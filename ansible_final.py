import subprocess

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

if __name__ == "__main__":
    showrun()