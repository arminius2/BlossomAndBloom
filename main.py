import argparse
import os
import subprocess
import threading
import requests
import keyring
import time
import signal
import daemon
from util.version_check import check_version
from zeroconf import ServiceInfo, Zeroconf
from httpserver import run_http_server

def handle_exit(signum, frame):
    print("Received termination signal. Exiting...")
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
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    check_internet_connection()
    check_version()
    start_firefox()

    PORT = 8081
    setup_zeroconf(PORT)

    http_server_thread = threading.Thread(target=run_http_server,args=(PORT,))
    http_server_thread.start()

    while True:
        time.sleep(100)

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
