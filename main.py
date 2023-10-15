import os
import subprocess
import threading
import requests
import keyring
import time
from util.version_check import check_version
import youtube_stream

streaming_pid = None  # Store the PID for the streaming process

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

def main():
    # Check internet connection first, block until it's available
    check_internet_connection()

    # Check if the current version matches the GitHub version
    check_version()

    # EXECUTE
    subprocess.run(["killall", "-9", "Firefox"])
    subprocess.run(["/Applications/Firefox.app/Contents/MacOS/firefox","-kiosk","https://www.canva.com/design/DAFsgM9Xi3A/Hsku1dC2x83Us3gMe25DWw/view?utm_content=DAFsgM9Xi3A&utm_campaign=designshare&utm_medium=link&utm_source=publishsharelink"])


if __name__ == "__main__":
    main()
