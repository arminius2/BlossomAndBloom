import json
import os
import argparse

class AppSettings:

    def __init__(self, settings_file_path='/home/pi/.config/BlossomApp/settings.json'):
        self.settings_file_path = settings_file_path
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file_path):
            with open(self.settings_file_path, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = {
                'youtube_api_key': '',
                'stream_schedule': '9-9:45am every Saturday',
                'announcements_url': 'http://example.com/announcements',
                'update_interval': 3600,
                'stream_source': None
            }
            os.makedirs(os.path.dirname(self.settings_file_path), exist_ok=True)
            self.save_settings()

    def save_settings(self):
        with open(self.settings_file_path, 'w') as f:
            json.dump(self.settings, f)

    def get_update_interval(self):
        return self.settings.get('update_interval', 3600)

    def set_update_interval(self, interval):
        self.settings['update_interval'] = interval
        self.save_settings()

    def get_stream_key(self):
        return self.settings.get('stream_key', '')

    def set_stream_key(self, key):
        self.settings['stream_key'] = key
        self.save_settings()

    def get_stream_source(self):
        return self.settings.get('stream_source', None)

    def set_stream_source(self, source):
        self.settings['stream_source'] = source
        self.save_settings()

    def show_all_settings(self):
        for key, value in self.settings.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage App Settings")
    parser.add_argument('--update-interval', type=int, help="Set the update interval")
    parser.add_argument('--stream-key', type=str, help="Set the stream key")
    parser.add_argument('--stream-source', type=str, help="Set the stream source")
    args = parser.parse_args()

    app_settings = AppSettings()

    if args.update_interval:
        app_settings.set_update_interval(args.update_interval)
    
    if args.stream_key:
        app_settings.set_stream_key(args.stream_key)

    if args.stream_source:
        app_settings.set_stream_source(args.stream_source)

    print("Current settings:")
    app_settings.show_all_settings()
