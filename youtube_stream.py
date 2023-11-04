import subprocess
import keyring
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from StreamingAppController import StreamingAppController

class YouTubeCredentialsManager:
    def __init__(self, service_name='BlossomAndBloom'):
        self.service_name = service_name
        self.credentials_file_path = 'credentials.json'

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

def start_stream():
    stream_manager = YouTubeStreamManager()     
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

def get_youtube_client():
    # Your OAuth 2.0 Client ID JSON file path
    client_secrets_file = "credentials.json"

    # Write Credentials to file
    credentials_manager = YouTubeCredentialsManager()
    credentials_manager.credentials_file_path = client_secrets_file
    credentials_manager.generate_credentials_file()

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