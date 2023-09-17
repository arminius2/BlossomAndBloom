#!/bin/bash

# Check if running as superuser
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Install required packages
apt update && apt install -y python3 python3-pip git
pip3 install PyQt5 requests

# Clone your repo (replace with your actual repo URL)
git clone https://github.com/arminius2/BlossomAndBloom.git /home/pi/BlossomApp

# Add a desktop shortcut
echo "[Desktop Entry]
Version=1.0
Name=Blossom and Bloom
Exec=python3 /home/pi/BlossomApp/Blossom.py
Icon=/home/pi/BlossomApp/icon.png
Terminal=false
Type=Application
" > /home/pi/Desktop/Blossom.desktop

# Make it executable
chmod +x /home/pi/Desktop/Blossom.desktop

# Enable auto-start (create an autostart folder if it doesn't exist)
mkdir -p /home/pi/.config/autostart
cp /home/pi/Desktop/Blossom.desktop /home/pi/.config/autostart/

echo "Installation complete."
