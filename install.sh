#!/bin/bash

set -e  # Stop the script if any command fails

echo "Starting Blossom and Bloom installation..."

# Load the new version from the repository
NEW_VERSION=$(cat /home/pi/BlossomApp/version.txt)

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))")

if [[ "$PYTHON_VERSION" < "3.7" ]]; then
    echo "Python 3.7 or greater is required. Please upgrade."
    exit 1
fi
echo "Python version OK."

# Check if running as superuser
echo "Checking for root permissions..."
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi
echo "Root permissions OK."

# Update package list
echo "Updating package list..."
apt-get update || { echo "Package list update failed! Aborting..."; exit 1; }
echo "Package list updated."

# Install required packages
echo "Installing required packages..."
apt-get install -y python3 python3-pip git python3-pyqt5 pi-bluetooth python3-bluez || { echo "Package installation failed! Aborting..."; exit 1; }
echo "Required packages installed."

# Remove the existing app directory if it exists
echo "Checking for existing installation..."
if [ -d "/home/pi/BlossomApp" ]; then
    echo "Removing existing installation..."
    rm -rf /home/pi/BlossomApp
fi
echo "Existing installation removed (if any)."

# Clone the repository
echo "Cloning the repository..."
git clone https://github.com/arminius2/BlossomAndBloom.git /home/pi/BlossomApp || { echo "Repository cloning failed! Aborting..."; exit 1; }
echo "Repository cloned."

# Navigate to the app directory
cd /home/pi/BlossomApp

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r /home/pi/BlossomApp/requirements.txt || { echo "Python dependency installation failed! Aborting..."; exit 1; }
echo "Python dependencies installed."

# Make Blossom.py executable
echo "Making Blossom.py executable..."
chmod +x Blossom.py || { echo "Making Blossom.py executable failed! Aborting..."; exit 1; }
echo "Blossom.py is now executable."

# Change owner of all files to 'pi' user
echo "Changing file ownership..."
chown -R pi:pi /home/pi/BlossomApp || { echo "Changing ownership failed! Aborting..."; exit 1; }
echo "File ownership changed."

# Create or update the Desktop shortcut
echo "Checking for Desktop shortcut..."
if [ -f /home/pi/Desktop/BlossomApp.desktop ]; then
  # Extract the existing version from the shortcut
  EXISTING_VERSION=$(grep '^Version=' /home/pi/Desktop/BlossomApp.desktop | cut -d '=' -f 2)
  
  # Check if the existing version matches the new version
  if [ "$EXISTING_VERSION" != "$NEW_VERSION" ]; then
    echo "Version mismatch. Updating the desktop shortcut..."
    rm -f /home/pi/Desktop/BlossomApp.desktop
  else
    echo "Desktop shortcut is up to date."
  fi
fi

# If the shortcut was removed or never existed, create it
if [ ! -f /home/pi/Desktop/BlossomApp.desktop ]; then
  echo "Creating new desktop shortcut with version $NEW_VERSION..."
  echo "[Desktop Entry]
  Version=$NEW_VERSION
  Name=Blossom and Bloom
  Comment=Start the Blossom and Bloom application
  Exec=python3 /home/pi/BlossomApp/Blossom.py
  Icon=/home/pi/BlossomApp/icon.png
  Terminal=false
  Type=Application
  Categories=Utility;Application;" > /home/pi/Desktop/BlossomApp.desktop
  
  # Make it executable
  chmod +x /home/pi/Desktop/BlossomApp.desktop || { echo "Making desktop shortcut executable failed! Aborting..."; exit 1; }
fi
echo "Desktop shortcut created."

# Check if the app is already set to auto-open on boot
echo "Setting up auto-open on boot..."
if ! grep -q "Blossom.py" /etc/xdg/lxsession/LXDE-pi/autostart; then
    # Auto-open the app on boot
    echo "@python3 /home/pi/BlossomApp/Blossom.py" >> /etc/xdg/lxsession/LXDE-pi/autostart || { echo "Setting up auto-open on boot failed! Aborting..."; exit 1; }
fi
echo "Auto-open on boot set up."

# Done
echo "Installation completed."
