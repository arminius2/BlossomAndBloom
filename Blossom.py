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
import sys

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
            self.show_menu()
            choice = input("Enter your choice: ").strip().lower()

            if choice.endswith(' -h'):
                command = choice[:-3]  # Remove ' -h' to get the actual command
                self.show_help_for_command(command)
                continue

            if choice == 'start':
                self.start_command()
            elif choice == 'stop':
                self.stop_command()
            elif choice == 'settings':
                self.print_app_settings()
            elif choice == 'check-update':
                self.check_for_update()
            elif choice == 'update':
                self.update_app()
            elif choice == 'list-sources':
                self.print_stream_sources()                
            elif choice == "exit":
                print("Exiting...")
                sys.exit(0)  # This will terminate the application            
            else:
                print("Invalid command")

    def show_menu(self):
        print("\n===== Blossom CLI Menu =====")
        print("{:<15} {:<40}".format("Command", "Description"))
        print("=" * 55)
        print("{:<15} {:<40}".format("start", "Start the Blossom application"))
        print("{:<15} {:<40}".format("stop", "Stop the Blossom application"))
        print("{:<15} {:<40}".format("settings", "Open the settings menu"))
        print("{:<15} {:<40}".format("check-update", "Check for updates"))
        print("{:<15} {:<40}".format("update", "Update the Blossom application"))
        print("{:<15} {:<40}".format("list-sources", "List available stream sources"))
        print("{:<15} {:<40}".format("exit", "Exit the application"))
        print("=" * 55)

    def print_stream_sources(self):
        print("Fetching available stream sources...")
        self.stream_source_manager.print_all_devices()  # Assuming this method exists in your StreamSource class and prints all the stream sources.        

    def start_command(self):
        print("Starting the Blossom application...")
        self.start_stream()

    def stop_command(self):
        print("Stopping the Blossom application...")
        self.stop_stream()

    def print_app_settings(self):
        print("Application Settings:")
        print(f"Stream Key: {self.app_settings.get_stream_key()}")
        print(f"Stream Source: {self.app_settings.get_stream_source()}")
        # Add more settings here as needed

    def check_for_update(self):
        print("Checking for updates...")
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

    def show_help_for_command(self, command):
        help_methods = {
            'start': self.help_start_command,
            'stop': self.help_stop_command,
            'settings': self.help_settings_command,
            'check-update': self.help_check_update_command,
            'update': self.help_update_command,
            'list-sources': self.help_list_sources_command,
        }
        if command in help_methods:
            help_methods[command]()
        else:
            print(f"No help topic for '{command}'")

    def help_start_command(self):
        print("Help topic for Start: Starts the Blossom application.")

    def help_stop_command(self):
        print("Help topic for Stop: Stops the Blossom application.")

    def help_settings_command(self):
        print("Help topic for Settings: Opens the settings menu to configure the application.")

    def help_check_update_command(self):
        print("Help topic for Check-Update: Checks for available updates.")

    def help_update_command(self):
        print("Help topic for Update: Updates the Blossom application to the latest version.")

    def help_list_sources_command(self):
        print("Help topic for List-Sources: Lists all the available stream sources.")

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
 