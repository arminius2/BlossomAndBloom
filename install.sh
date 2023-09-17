#!/bin/bash

PYTHON_VERSION=$(python3 -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))")

if [[ "$PYTHON_VERSION" < "3.7" ]]; then
    echo "Python 3.7 or greater is required. Please upgrade."
    exit 1
fi

# Check if running as superuser
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Update package list
apt-get update

# Install required system packages
apt-get install -y python3 python3-pip git python3-pyqt5

# Remove the existing app directory if it exists
if [ -d "/home/pi/BlossomApp" ]; then
    rm -rf /home/pi/BlossomApp
fi

# Clone the repository
git clone https://github.com/arminius2/BlossomAndBloom.git /home/pi/BlossomApp

# Navigate to the app directory
cd /home/pi/BlossomApp

# Install required Python packages
pip3 install requests Pylivestream

# Make Blossom.py executable
chmod +x Blossom.py

# Change owner of all files to 'pi' user
chown -R pi:pi /home/pi/BlossomApp

# Check if the shortcut is already present on the desktop
if [ ! -f /home/pi/Desktop/BlossomApp.desktop ]; then
  # Create a Desktop shortcut
  echo "[Desktop Entry]
  Version=1.0
  Name=Blossom and Bloom
  Comment=Start the Blossom and Bloom application
  Exec=python3 /home/pi/BlossomApp/Blossom.py
  Icon=/home/pi/BlossomApp/icon.png
  Terminal=false
  Type=Application
  Categories=Utility;Application;" > /home/pi/Desktop/BlossomApp.desktop
fi

# Make it executable
chmod +x /home/pi/Desktop/BlossomAndBloom.desktop

# Check if the app is already set to auto-open on boot
if ! grep -q "Blossom.py" /etc/xdg/lxsession/LXDE-pi/autostart; then
    # Auto-open the app on boot
    echo "@python3 /home/pi/BlossomApp/Blossom.py" >> /etc/xdg/lxsession/LXDE-pi/autostart
fi

# Done
echo "Installation completed."