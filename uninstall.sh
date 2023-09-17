#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root."
    exit 1
fi

# Remove the BlossomApp directory if it exists
if [ -d "/home/pi/BlossomApp" ]; then
    rm -rf /home/pi/BlossomApp
    echo "Removed /home/pi/BlossomApp"
fi

# Remove the desktop shortcut if it exists
if [ -f "/home/pi/Desktop/BlossomAndBloom.desktop" ]; then
    rm /home/pi/Desktop/BlossomAndBloom.desktop
    echo "Removed desktop shortcut"
fi

# Remove the auto-open on boot
if grep -q "Blossom.py" /etc/xdg/lxsession/LXDE-pi/autostart; then
    sed -i '/Blossom.py/d' /etc/xdg/lxsession/LXDE-pi/autostart
    echo "Removed from auto-open on boot"
fi

# Done
echo "Uninstallation completed."
