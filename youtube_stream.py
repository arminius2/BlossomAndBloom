import subprocess
import keyring

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
