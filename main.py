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
import youtube_stream
from zeroconf import ServiceInfo, Zeroconf
from httpserver import run_http_server

streaming_pid = None  # Store the PID for the streaming process

def handle_exit(signum, frame):
    print("Received termination signal. Exiting...")
    if streaming_pid is not None:
        stop_youtube_stream()
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

def toggle_youtube_stream():
    global streaming_pid
    if not check_stream_key():
        print("No YouTube stream key set.")
        return

    if streaming_pid is None:
        start_youtube_stream()
    else:
        stop_youtube_stream()

def start_youtube_stream():
    global streaming_pid
    if streaming_pid is not None:
        print("Stream already running.")
        return

    # Start youtube_stream.py in a new thread
    stream_thread = threading.Thread(target=youtube_stream.start_stream)
    stream_thread.start()

    # Stash the thread's PID (for demonstration)
    streaming_pid = stream_thread.ident

def stop_youtube_stream():
    global streaming_pid
    if streaming_pid is None:
        print("No stream is running.")
        return

    # Stop the streaming process
    youtube_stream.stop_stream()
    streaming_pid = None

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
                 PORT, 0, 0, {}})
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
