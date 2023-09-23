import threading
import time
import requests
import os
from PyQt5.QtCore import Qt, pyqtSignal

class UpdateChecker:
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, update_interval, version_file_path, version_url):
        self.update_interval = update_interval  # seconds
        self.version_file_path = version_file_path
        self.version_url = version_url
        self.latest_version = None
        self.last_checked = None
        self.current_version = self.read_current_version()
        self.update_thread = threading.Thread(target=self.run)
        self.lock = threading.Lock()  # For thread-safe operations
        self.update_thread.start()

    def read_current_version(self):
        try:
            with open(self.version_file_path, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            print(f"Version file {self.version_file_path} not found.")
            return None

    def run(self):
        while True:
            self.check_for_update()
            time.sleep(self.update_interval)

    def check_for_update(self):
        try:
            response = requests.get(self.version_url)
            latest_version = response.text.strip()
            with self.lock:
                self.latest_version = latest_version
                self.last_checked = time.time()
            if self.current_version < self.latest_version:
                print("Update available!")
                self.new_version_signal.emit(latest_version)
        except Exception as e:
            print(f"An error occurred while checking for updates: {e}")

    def get_last_checked(self):
        with self.lock:
            return self.last_checked

    def get_latest_version(self):
        with self.lock:
            return self.latest_version
