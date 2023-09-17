#!/bin/bash

# Check if running as superuser
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Update package list
apt-get update

# Install required system packages
apt-get install -y python3 python3-pip git

# Remove the existing app directory if it exists
if [ -d "/home/pi/BlossomApp" ]; then
    rm -rf /home/pi/BlossomApp
fi

# Clone the repository
git clone https://github.com/arminius2/BlossomAndBloom.git /home/pi/BlossomApp

# Navigate to the app directory
cd /home/pi/BlossomApp

# Install required Python packages
pip3 install PyQt5 requests Pylivestream

# Make Blossom.py executable
chmod +x Blossom.py

# Change owner of all files to 'pi' user
chown -R pi:pi /home/pi/BlossomApp

# Add desktop shortcut
echo "[Desktop Entry]
Type=Application
Name=Blossom and Bloom
Exec=python3 /home/pi/BlossomApp/Blossom.py
Icon=/home/pi/BlossomApp/icon.png
" > /home/pi/Desktop/BlossomAndBloom.desktop

# Make it executable
chmod +x /home/pi/Desktop/BlossomAndBloom.desktop

# Check if the app is already set to auto-open on boot
if ! grep -q "Blossom.py" /etc/xdg/lxsession/LXDE-pi/autostart; then
    # Auto-open the app on boot
    echo "@python3 /home/pi/BlossomApp/Blossom.py" >> /etc/xdg/lxsession/LXDE-pi/autostart
fi

# Done
echo "Installation completed."