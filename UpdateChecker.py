from PyQt5.QtCore import QThread, pyqtSignal
import requests

class UpdateChecker(QThread):
    signal = pyqtSignal('PyQt_PyObject')
    
    def __init__(self, interval):
        super().__init__()
        self.interval = interval
    
    def run(self):
        while True:
            # Check version
            with open('/home/pi/BlossomApp/version.txt', 'r') as f:
                current_version = f.read().strip()

            response = requests.get("https://api.github.com/repos/arminius2/BlossomAndBloom/releases/latest")
            latest_version = response.json().get('tag_name', '0.0.0')
            
            if latest_version != current_version:
                self.signal.emit(True)
            
            # Sleep
            QThread.sleep(self.interval)