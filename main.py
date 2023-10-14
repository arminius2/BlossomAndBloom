import os
import subprocess
import youtube_stream

from util.version_check import check_version

def check_version():
    # This is where we'd normally use the function from version_check.py
    # For demonstration, let's just print a message
    print("Checking version...")
    check_version()

def execute_ffmpeg_command():
    # This is where we'd normally use the function from ffmpeg_command.py
    # For demonstration, let's just print a message
    print("Executing FFmpeg command...")

def launch_gui():
    # This is where we'd normally launch the GUI
    # For demonstration, let's just print a message
    print("Launching GUI...")

def main():
    # Check if the current version matches the GitHub version
    check_version()
    
    # Initialize modules like pyatv and start FFmpeg command for YouTube streaming
    execute_ffmpeg_command()

    # Launch the GUI
    launch_gui()

if __name__ == "__main__":
    main()
