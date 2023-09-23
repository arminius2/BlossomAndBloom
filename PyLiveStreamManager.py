import subprocess
import time
import configparser
import psutil

class PyLiveStreamManager:

    def __init__(self, stream_key, stream_source):
        self.stream_key = stream_key
        self.stream_source = stream_source
        self.stream_process = None

    def create_ini_file(self):
        config = configparser.ConfigParser()
        config['YouTube'] = {'Key': self.stream_key, 'Source': self.stream_source}
        with open('youtube_stream.ini', 'w') as configfile:
            config.write(configfile)

    def check_if_stream_is_running(self):
        for process in psutil.process_iter(['pid', 'name']):
            if "ffmpeg" in process.info['name']:
                return True
        return False

    def start_stream(self):
        self.create_ini_file()
        self.stream_process = subprocess.Popen(["PyLivestream", "youtube_stream.ini"])

    def stop_stream(self):
        if self.stream_process:
            self.stream_process.terminate()
            self.stream_process = None

    def monitor_stream(self):
        try:
            while True:
                if self.check_if_stream_is_running():
                    print("Stream is running...")
                else:
                    print("Stream has stopped.")
                    break
                time.sleep(5)
        except KeyboardInterrupt:
            print("Stopping the stream...")
            self.stop_stream()


if __name__ == "__main__":
    stream_key = input("Enter your YouTube stream key: ")
    stream_source = input("Enter your stream source (camera/screen): ")
    manager = PyLiveStreamManager(stream_key, stream_source)
    manager.start_stream()
    manager.monitor_stream()