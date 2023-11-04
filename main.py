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
import json
import urllib.parse
from util.version_check import check_version
from zeroconf import ServiceInfo, Zeroconf
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from StreamingAppController import StreamingAppController
from http.server import HTTPServer, BaseHTTPRequestHandler

running = True
streaming_thread_identifier = None
streaming = False

class MyHTTPHandler(BaseHTTPRequestHandler):
     def do_GET(self):
        global streaming  # Declare streaming as globyhh   al to modify it

        print(f"[HTTPServer] incoming GET " + self.path)

        # If the path is '/toggle', toggle the streaming state
        if self.path == '/toggle':
            streaming = not streaming

            print(f"[HTTPServer] Streaming state toggled: {'ON' if streaming else 'OFF'}")

            # Redirect back to the root path
            self.send_response(303)  # 303 See Other
            self.send_header('Location', '/')
            self.end_headers()
            if streaming:
                start_youtube_stream()
            else:
                stop_youtube_stream()
        
        # Otherwise, just display the state
        else:
            print(f"[HTTPServer] Displaying state...")
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            message = f"<html><body>Streaming is {'ON' if streaming else 'OFF'}<br><a href='/toggle'>Toggle Stream</a></body></html>"
            self.wfile.write(message.encode('utf-8'))

class YouTubeStreamManager:
    _instance = None
    app_controller = None
    current_stream_url = None
    check_interval = 300  # Check every 5 minutes

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(YouTubeStreamManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # This will only happen once
            self.initialized = True
            self.streaming_url = None
            self.app_controller = None

    def update_stream_url(self, new_url):
        if new_url != self.streaming_url:
            self.streaming_url = new_url
            # If there's an active window, tear it down
            if self.app_controller:
                self.app_controller.tearDownWindow()
            # Setup new window with the new URL
            self.app_controller = StreamingAppController(new_url)
            self.app_controller.setupWindow()

    @classmethod
    def check_stream_status(cls, youtube_client):
        try:
            request = youtube_client.liveBroadcasts().list(
                broadcastStatus="active",
                part="snippet,contentDetails"
            )
            response = request.execute()

            if "items" in response:
                for item in response["items"]:
                    stream_url = item["contentDetails"]["monitorStream"]["embedHtml"]
                    if cls.current_stream_url != stream_url:
                        if cls.app_controller:
                            cls.app_controller.tearDownWindow()
                        cls.current_stream_url = stream_url
                        cls.app_controller = StreamingAppController(stream_url)
                        cls.app_controller.run()
                    # If the URL hasn't changed, there's no need to do anything
            else:
                print("No active streams found.")
                if cls.app_controller:
                    cls.app_controller.tearDownWindow()
                    cls.app_controller = None
                cls.current_stream_url = None
        except Exception as e:
            print(f"An error occurred: {e}")

        # Schedule the next check
        threading.Timer(cls.check_interval, cls.start_youtube_stream).start()

    @classmethod
    def start_youtube_stream(cls):
        youtube_client = get_youtube_client()
        cls.check_stream_status(youtube_client)

class YouTubeCredentialsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(YouTubeCredentialsManager, cls).__new__(cls)
            # Initialize the object here if needed
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, service_name='BlossomAndBloom'):
        if not self.__initialized:
            self.service_name = service_name
            self.credentials_file_path = 'credentials.json'
            self.__initialized = True

    def get_api_key(self):
        return keyring.get_password(self.service_name, 'YouTubeAPIKey')

    def get_client_id(self):
        return keyring.get_password(self.service_name, 'YouTubeClientID')

    def get_client_secret(self):
        return keyring.get_password(self.service_name, 'YouTubeClientSecret')

    def save_to_keyring(self, api_key, client_id, client_secret):
        keyring.set_password(self.service_name, 'YouTubeAPIKey', api_key)
        keyring.set_password(self.service_name, 'YouTubeClientID', client_id)
        keyring.set_password(self.service_name, 'YouTubeClientSecret', client_secret)

    def generate_credentials_file(self):
        credentials_dict = {
            "installed": {
                "client_id": self.get_client_id(),
                "project_id": "blossomandbloomtest",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": self.get_client_secret(),
                "redirect_uris": [
                    "urn:ietf:wg:oauth:2.0:oob",
                    "http://localhost"
                ]
            }
        }

        with open(self.credentials_file_path, 'w') as credentials_file:
            json.dump(credentials_dict, credentials_file, indent=4)

        print(f'Credentials written to {self.credentials_file_path}')

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

#   Start / Stop Local Stream

def start_stream():
    stream_key = keyring.get_password("BlossomAndBloom", "YouTubeStream")
    ffmpeg_command = [
        'ffmpeg',
        '-hide_banner',
        '-loglevel', 'verbose',
        '-f', 'avfoundation',
        '-framerate', '30',
        '-probesize', '42M',
        '-pix_fmt', 'uyvy422',
        '-video_size', '1920x1080',
        '-i', '0:0',
        '-vcodec', 'libx264',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-f', 'flv',
        f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    ]

    is_recording = True  # assuming the device starts in recording mode

    # Kickstart the YouTubeStreamManager to start the stream window
    stream_manager.start_youtube_stream()  # Assuming this method prepares the window

    try:
        with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True) as proc:
            print("Stream started...")

            # Process ffmpeg output in real-time
            for line in iter(proc.stdout.readline, ''):
                print(line.strip())

                # You could implement some logic here to stop the recording based on some condition
                # For example, if a "stop" command is detected in the output
                if "stop condition" in line:
                    break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # When stopping the stream, kick the YouTubeStreamManager to tear down the stream window
        stream_manager.teardown_stream_window()  # Assuming this method tears down the window

        print("Stream has ended.")

# HTTP Server

def run_http_server(PORT):
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MyHTTPHandler)
    httpd.serve_forever()        

# Youtube Stream Management 

def get_youtube_client():
    # Your OAuth 2.0 Client ID JSON file path
    client_secrets_file = "credentials.json"

    # Write Credentials to file
    YouTubeCredentialsManager().credentials_file_path = client_secrets_file
    YouTubeCredentialsManager().generate_credentials_file()

    # Check if credentials exist
    credentials = Credentials.from_authorized_user_file("credentials.json", ["https://www.googleapis.com/auth/youtube.force-ssl"])    

    youtube = build("youtube", "v3", credentials=credentials)

    return youtube

def get_streaming_url():
    request = get_youtube_client().liveBroadcasts().list(
        broadcastStatus="active",
        part="snippet,contentDetails"
    )
    response = request.execute()
    
    if "items" in response:
        for item in response["items"]:
            print("Streaming URL:", item["contentDetails"]["monitorStream"]["embedHtml"])
    else:
        print("No active streams found.")  

#   Start / Stop Youtube Stream

def toggle_youtube_stream():
    global streaming_thread_identifier
    if streaming_thread_identifier is None:
        start_youtube_stream()
    else:
        stop_youtube_stream()

def start_youtube_stream():
    global streaming_thread_identifier
    if streaming_thread_identifier is not None:
        print("Stream already running.")
        return

    # Start youtube_stream.py in a new thread
    stream_thread = threading.Thread(target=start_stream)
    stream_thread.start()
    streaming_thread_identifier = stream_thread.ident

def stop_youtube_stream():
    global streaming_thread_identifier
    if streaming_thread_identifier is None:
        print("No stream is running.")
        return

    stop_stream()
    streaming_thread_identifier = None

#   Main Program

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
