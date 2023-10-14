import os
import requests
import subprocess

def get_remote_version():
    url = 'https://raw.githubusercontent.com/arminius2/BlossomAndBloom/main/version.txt'
    response = requests.get(url)
    return response.text.strip()

def get_local_version():
    with open(os.path.expanduser("~/.blossomandbloom/version.txt"), 'r') as file:
        return file.read().strip()

def update_install_script():
    subprocess.run(['sudo', os.path.expanduser("~/.blossomandbloom/install.sh")])

def check_version():
    local_version = get_local_version()
    remote_version = get_remote_version()

    if local_version != remote_version:
        print("New version available. Updating...")
        update_install_script()

if __name__ == "__main__":
    check_version()
