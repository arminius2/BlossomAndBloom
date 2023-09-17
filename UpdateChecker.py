import requests
import time
from PyQt5.QtCore import Qt, pyqtSignal

class UpdateChecker:
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, interval, current_version):
        self.interval = interval
        self.current_version = current_version

    def check_update(self):
        try:
            response = requests.get("https://raw.githubusercontent.com/arminius2/BlossomAndBloom/main/version.txt")
            latest_version = response.text.strip()
            if latest_version != self.current_version:
                print(f"New version available: {latest_version}")
                self.new_version_signal.emit(latest_version)
            else:
                print("You are running the latest version.")
        except Exception as e:
            print(f"An error occurred while checking for updates: {e}")

    def run(self):
        while True:
            self.check_update()
            time.sleep(self.interval)