import os
import subprocess
import threading
import requests
import keyboard
import time
from util.version_check import check_version
import youtube_stream

streaming_pid = None  # Store the PID for the streaming process
thread_running = 1

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

def launch_gui():
    print("Launching GUI...")

def setup_appletv_remote():
    print("Setting up AppleTV remote...")

def exit():
    global thread_running
    thread_running = 0

def main():
    # Check internet connection first, block until it's available
    check_internet_connection()

    # Check if the current version matches the GitHub version
    check_version()

    # Launch the GUI
    launch_gui()

    keyboard.on_press_key("space", toggle_youtube_stream)
    keyboard.on_press_key("q", exit)

    global thread_running
    while thread_running:
      time.sleep(0.1)



if __name__ == "__main__":
    main()
