from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from AppSettings import AppSettings
from UpdateChecker import UpdateChecker
import os

class BlossomApp(QWidget):
    
    def __init__(self):
        super(BlossomApp, self).__init__()
        
        self.app_settings = AppSettings()

        # GUI setup
        self.setWindowTitle("Blossom and Bloom")
        
        layout = QVBoxLayout()
        self.streamButton = QPushButton("Start Stream")
        layout.addWidget(self.streamButton)
        
        self.label = QLabel("Stream Status: Not Started")
        layout.addWidget(self.label)
        
        self.setLayout(layout)
        
        self.streaming = False
        
        self.streamButton.clicked.connect(self.toggle_stream)
        
        self.update_checker = UpdateChecker(self.app_settings.settings['update_interval'])
        self.update_checker.signal.connect(self.update_app)
        self.update_checker.start()

    def toggle_stream(self):
        if self.streaming:
            self.stop_stream()
        else:
            self.start_stream()
        
    def start_stream(self):
        print("Stream started")
        self.label.setText("Stream Status: Running")
        self.streamButton.setText("Stop Stream")
        self.streaming = True
        
    def stop_stream(self):
        print("Stream stopped")
        self.label.setText("Stream Status: Not Started")
        self.streamButton.setText("Start Stream")
        self.streaming = False
                
    def update_app(self, update_available):
        if update_available:
            os.system('bash /home/pi/BlossomApp/install.sh')
            QApplication.quit()

if __name__ == "__main__":
    app = QApplication([])
    window = BlossomApp()
    window.show()
    app.exec_()