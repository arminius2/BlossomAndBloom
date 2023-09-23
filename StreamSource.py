import os
import re
import subprocess
import threading

class VideoDeviceInfo:
    def __init__(self, video_device):
        self.video_device = video_device
        self.driver_name = None
        self.card_type = None
        self.bus_info = None
        self.driver_version = None
        self.width = None
        self.height = None
        self.pixel_format = None
        self.populate_additional_info()

    def populate_additional_info(self):
        cmd_output = subprocess.getoutput(f"v4l2-ctl --all --device {self.video_device}")
        try:
            self.driver_name = re.search("Driver name\s*:\s*(.+)", cmd_output).group(1)
            self.card_type = re.search("Card type\s*:\s*(.+)", cmd_output).group(1)
            self.bus_info = re.search("Bus info\s*:\s*(.+)", cmd_output).group(1)
            self.driver_version = re.search("Driver version\s*:\s*(.+)", cmd_output).group(1)
            self.width = int(re.search("Width/Height\s*:\s*(\d+)/(\d+)", cmd_output).group(1))
            self.height = int(re.search("Width/Height\s*:\s*(\d+)/(\d+)", cmd_output).group(2))
            self.pixel_format = re.search("Pixel Format\s*:\s*'(.+)'", cmd_output).group(1)
        except AttributeError:
            print(f"Failed to extract some attributes for {self.video_device}")

    def get_resolution(self):
        return self.width * self.height if self.width and self.height else 0

class StreamDevice:
    def __init__(self, device_id, media_devices, video_devices):
        self.device_id = device_id
        self.media_devices = media_devices
        self.video_device_info = [VideoDeviceInfo(video_device) for video_device in video_devices]

    def is_camera(self):
        return any("camera" in info.card_type.lower() for info in self.video_device_info)

    def is_usb_video_capture(self):
        return any("usb video" in info.card_type.lower() for info in self.video_device_info)

    def get_resolution(self):
        return max(info.get_resolution() for info in self.video_device_info)

class StreamSource:
    def __init__(self, app_settings):
        self.app_settings = app_settings
        self.lock = threading.Lock()
        self.devices = self.find_stream_source()

    def find_stream_source(self):
        devices = []
        cmd_output = subprocess.getoutput("v4l2-ctl --list-devices")
        for device_block in cmd_output.split("\n\n"):
            lines = device_block.strip().split("\n")
            device_id = lines[0].strip()
            media_devices = [line.strip() for line in lines[1:] if "media" in line]
            video_devices = [line.strip() for line in lines[1:] if "video" in line]
            devices.append(StreamDevice(device_id, media_devices, video_devices))
        return devices

    def print_all_devices(self):
        print("Available Stream Source Devices:")
        print("{:<40} {:<60} {:<20} {:<15}".format("Device ID", "Associated Devices", "Resolution", "Pixel Format"))
        print("=" * 135)
        for device in self.devices:
            for video_info in device.video_device_info:
                print(f"{device.device_id:<40} {video_info.video_device:<60} {video_info.width}x{video_info.height:<20} {video_info.pixel_format:<15}")

    def get_best_camera_device(self):
        best_camera = None
        highest_resolution = 0

        for device in self.devices:
            if device.is_camera():
                resolution = device.get_resolution()
                if resolution > highest_resolution:
                    highest_resolution = resolution
                    best_camera = device

        return best_camera

    def get_best_usb_video_capture_device(self):
        best_usb_capture = None
        highest_resolution = 0

        for device in self.devices:
            if device.is_usb_video_capture():
                resolution = device.get_resolution()
                if resolution > highest_resolution:
                    highest_resolution = resolution
                    best_usb_capture = device

        return best_usb_capture

if __name__ == "__main__":
    stream_source = StreamSource()
    stream_source.print_all_devices()
    best_camera = stream_source.get_best_camera_device()
    best_usb = stream_source.get_best_usb_video_capture_device()
    print("Best Camera Device:", best_camera.device_id if best_camera else "None")
    print("Best USB Video Capture Device:", best_usb.device_id if best_usb else "None")
