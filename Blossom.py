from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QTextEdit
from PyQt5.QtCore import QTimer
import requests
import json
import sys
import subprocess

class AppSettings:
    def __init__(self):
        self.filename = "settings.json"
        self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {
                'youtube_api_key': "",
                'stream_schedule': {'day': 'Saturday', 'start': '9:00', 'end': '9:45'},
                'announcements_url': ""
            }
            self.save()

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

def execute_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return False

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = AppSettings()

        # Read the current version from a file
        with open("version.txt", "r") as f:
            self.current_version = f.read().strip()

        # Setup a timer to check for updates every hour
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_for_updates)
        self.timer.start(60 * 60 * 1000)  # 1 hour in milliseconds

        self.initUI()

    def initUI(self):
        # Initialize UI elements here
        self.setGeometry(100, 100, 640, 480)
        self.setWindowTitle('Blossom and Bloom')

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(50, 50, 400, 300)

        self.start_button = QPushButton("Start Stream", self)
        self.start_button.move(50, 400)
        self.start_button.clicked.connect(self.start_stop_stream)

        self.is_streaming = False

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Blossom and Bloom Streaming')
        self.show()

   def toggle_stream(self):
        if self.is_streaming:
            self.stop_stream()
        else:
            self.start_stream()

   def start_stream(self):
        # Using subprocess to start the PyLivestream
        self.process = subprocess.Popen(["PyLivestream", "YouTubeLive.ini"])
        print("Starting the stream...")
        self.stream_button.setText('Stop Stream')
        self.is_streaming = True

    def stop_stream(self):
        # Terminating the PyLivestream process
        self.process.terminate()
        print("Stopping the stream...")
        self.stream_button.setText('Start Stream')
        self.is_streaming = False


    def check_for_updates(self):
        try:
            # Fetch the latest version from GitHub
            response = requests.get("https://raw.githubusercontent.com/yourusername/yourrepo/main/version.txt")
            latest_version = response.text.strip()

            if self.current_version != latest_version:
                self.update_app(latest_version)
        except requests.RequestException:
            print("Could not check for updates.")

    def update_app(self, new_version):
        print(f"Updating app to version {new_version}")

        if not execute_command("git pull origin main"):
            print("Failed to update code from repository.")
            return

        if execute_command("python3 Blossom.py"):
            print("Successfully updated and restarted the app.")
            self.close()
        else:
            print("Failed to restart the app.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AppWindow()
    ex.show()
    sys.exit(app.exec_())
