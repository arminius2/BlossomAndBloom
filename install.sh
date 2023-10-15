#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

# Generate a UUID for a temporary directory
uuid=$(uuidgen)
tmp_dir="/tmp/blossomandbloom-$uuid"

# Clone the GitHub repository into the temporary directory
git clone https://github.com/arminius2/BlossomAndBloom.git $tmp_dir || exit 1

# Define the install directory
install_dir="$HOME/.blossomandbloom"

# Move from temporary directory to install directory
mv $tmp_dir $install_dir

# Navigate to the project directory
cd $install_dir || exit 1

# Install Python dependencies
pip3 install -r dependencies.txt

# Create a .plist file for launchd
plist_path=~/Library/LaunchAgents/com.blossomandbloom.plist

# Unload the existing agent, if present
launchctl bootout gui/$(id -u $(logname)) $plist_path || echo "No existing agent to unload."

# Create the new .plist content
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
  <key>Label</key>
  <string>com.blossomandbloom</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>$install_dir/main.py</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>" > $plist_path

# Set ownership and permissions
chmod 644 $plist_path
chown $(logname):$(id -gn $(logname)) $plist_path

# Load the new agent
launchctl bootstrap gui/$(id -u $(logname)) $plist_path

# Check if YouTube stream key is set
youtube_key=$(keyring get BlossomAndBloom YouTubeStream)

if [ -z "$youtube_key" ]; then
  echo "No YouTube stream key is set."
  echo -n "Please enter your YouTube stream key: "
  read -r stream_key

  python3 -c "import keyring; keyring.set_password('BlossomAndBloom', 'YouTubeStream', '$stream_key')"
fi

# Change ownership to the non-root user
chown -R $(logname):$(id -gn $(logname)) $install_dir

echo "Installation complete."
