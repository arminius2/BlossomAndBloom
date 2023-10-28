import subprocess
import keyring
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

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

    while is_recording:
        with subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True) as proc:
            for line in iter(proc.stdout.readline, ''):
                print(line)  # or

def get_youtube_client():
    api_key = keyring.get_password("BlossomAndBloom", "YouTubeAPIKey")
    oauth_client_id = keyring.get_password("BlossomAndBloom", "YouTubeClientID")
    oauth_client_secret = keyring.get_password("BlossomAndBloom", "YouTubeClientSecret")

    # Your OAuth 2.0 Client ID JSON file path
    client_secrets_file = "path/to/your/client_secret.json"

    # Check if credentials exist
    credentials = None
    if os.path.exists("credentials.json"):
        credentials = Credentials.from_authorized_user_file("credentials.json", ["https://www.googleapis.com/auth/youtube.force-ssl"])
    
    # If there are no (valid) credentials, prompt the user to log in
    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, ["https://www.googleapis.com/auth/youtube.force-ssl"])
        credentials = flow.run_console()
        with open("credentials.json", "w") as f:
            f.write(credentials.to_json())

    youtube = build("youtube", "v3", credentials=credentials)

    return youtube

def get_streaming_url(youtube):
    request = youtube.liveBroadcasts().list(
        broadcastStatus="active",
        part="snippet,contentDetails"
    )
    response = request.execute()
    
    if "items" in response:
        for item in response["items"]:
            print("Streaming URL:", item["contentDetails"]["monitorStream"]["embedHtml"])
    else:
        print("No active streams found.")    