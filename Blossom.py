import argparse
import PyQt5
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from AppSettings import AppSettings
from UpdateChecker import UpdateChecker
from PyLiveStreamManager import PyLiveStreamManager
from StreamSource import StreamSource
import threading
import os

# Common base class for shared functionality
class BlossomApplication:
    def __init__(self):
        self.streaming = False
        self.app_settings = AppSettings()
        self.update_checker = UpdateChecker(3600, "./version.txt", "https://raw.githubusercontent.com/arminius2/BlossomAndBloom/main/version.txt")
        self.stream_source_manager = StreamSource(self.app_settings)
        self.stream_manager = PyLiveStreamManager(self.app_settings.get_stream_key(), self.app_settings.get_stream_source())

    def start_stream(self):
        print("Stream started")
        self.streaming = True

    def stop_stream(self):
        print("Stream stopped")
        self.streaming = False

# GUI-specific implementation
class BlossomGUIApplication(QWidget, BlossomApplication):
    def __init__(self):
        QWidget.__init__(self)
        BlossomApplication.__init__(self)

        self.setWindowTitle("Blossom and Bloom")

        layout = QVBoxLayout()
        self.streamButton = QPushButton("Start Stream")
        layout.addWidget(self.streamButton)

        self.label = QLabel("Stream Status: Not Started")
        layout.addWidget(self.label)

        self.setLayout(layout)

        self.streamButton.clicked.connect(self.toggle_stream)

    def toggle_stream(self):
        if self.streaming:
            self.stop_stream()
            self.label.setText("Stream Status: Not Started")
            self.streamButton.setText("Start Stream")
        else:
            self.start_stream()
            self.label.setText("Stream Status: Running")
            self.streamButton.setText("Stop Stream")

# CLI-specific implementation
class BlossomCLIApplication(BlossomApplication):
    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            command = input("Enter 'start' to start the stream, 'stop' to stop the stream, 'settings' to view app settings, 'check-update' to check for updates, or 'update' to perform update: ")
            if command == 'start':
                self.start_stream()
            elif command == 'stop':
                self.stop_stream()
            elif command == 'settings':
                self.print_app_settings()
            elif command == 'check-update':
                self.check_for_update()
            elif command == 'update':
                self.update_app()
            else:
                print("Invalid command")

    def print_app_settings(self):
        print("Application Settings:")
        print(f"Stream Key: {self.app_settings.get_stream_key()}")
        print(f"Stream Source: {self.app_settings.get_stream_source()}")
        # Add more settings here as needed

    def check_for_update(self):
        update_available = self.update_checker.check_for_update()
        if update_available:
            print("An update is available.")
        else:
            print("You are running the latest version.")

    def update_app(self):
        update_available = self.update_checker.check_for_update()
        if update_available:
            print("Updating the application...")
            os.system('sudo bash /home/pi/BlossomApp/install.sh')
            print("Update complete.")
        else:
            print("You are running the latest version, no update required.")        

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description='Blossom Application')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    args = parser.parse_args()

    if args.cli:
        print("Running in CLI mode.")
        app = BlossomCLIApplication()
        app.run()
    else:
        print("Running in GUI mode.")
        app = QApplication([])
        window = BlossomGUIApplication()
        window.show()
        app.exec_()

if __name__ == "__main__":
    main()
 