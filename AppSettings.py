import json
import os

class AppSettings:

    def __init__(self):
        self.load_settings()

    def load_settings(self):
        settings_file = '/home/pi/.config/BlossomApp/settings.json'
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                'youtube_api_key': '',
                'stream_schedule': '9-9:45am every Saturday',
                'announcements_url': 'http://example.com/announcements',
                'update_interval': 3600
            }
            os.makedirs('/home/pi/.config/BlossomApp/', exist_ok=True)
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f)

    def get_update_interval(self):
         return self.settings.get('update_interval', 3600)