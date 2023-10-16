import argparse
import os
import subprocess
import threading
import requests
import keyring
import time
import signal
import fcntl
import daemon
from util.version_check import check_version
from zeroconf import ServiceInfo, Zeroconf
from httpserver import run_http_server

running = True

def handle_exit(signum, frame):
    global running
    print("Received termination signal. Exiting...")
    running = False
    os._exit(0)

def check_stream_key():
    stream_key = keyring.get_password('BlossomAndBloom', 'YouTubeStream')
    if stream_key is None:
        print("No YouTube stream key is set.")
        return False
    else:
        return True

def check_internet_connection():
    print("Checking internet connection...")
    while True:
        try:
            requests.get('https://www.youtube.com', timeout=5)
            print("Internet connection available.")
            break
        except requests.ConnectionError:
            print("No internet connection. Retrying in 5 seconds...")
            time.sleep(5)

def start_firefox():
    subprocess.run(["killall", "-9", "Firefox"])
    subprocess.run([
        "/Applications/Firefox.app/Contents/MacOS/firefox",
        "-kiosk",
        "https://www.canva.com/design/DAFsgM9Xi3A/Hsku1dC2x83Us3gMe25DWw/view?utm_content=DAFsgM9Xi3A&utm_campaign=designshare&utm_medium=link&utm_source=publishsharelink"
    ])

def setup_zeroconf(PORT):
    zeroconf = Zeroconf()
    wsInfo = ServiceInfo('_http._tcp.local.',
                 "blossomandbloom._http._tcp.local.",
                 PORT, 0, 0, {})
    zeroconf.register_service(wsInfo)

def main_program():
    lock_file_path = 'program.lock'
    
    # Try to acquire the lock
    try:
        lock_file = open(lock_file_path, 'w')
        fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Another instance of the program is already running. Exiting...")
        return

    # Register the lock release for program termination
    def release_lock():
        fcntl.lockf(lock_file, fcntl.LOCK_UN)
        lock_file.close()
        os.remove(lock_file_path)
    
    signal.signal(signal.SIGTERM, lambda signum, frame: (handle_exit(signum, frame), release_lock()))
    signal.signal(signal.SIGINT, lambda signum, frame: (handle_exit(signum, frame), release_lock()))

    check_internet_connection()
    check_version()
    start_firefox()

    PORT = 8081
    setup_zeroconf(PORT)

    http_server_thread = threading.Thread(target=run_http_server,args=(PORT,))
    http_server_thread.start()

    while running:
        time.sleep(10)

    release_lock()         

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the program.')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')

    args = parser.parse_args()

    if args.daemon:
        # Run as a daemon
        with daemon.DaemonContext(
            working_directory=os.getcwd(),
            stdout=open("stdout.log", "w+"),
            stderr=open("stderr.log", "w+")
        ):
            main_program()
    else:
        # Run normally
        main_program()
