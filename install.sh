#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

# Killing all instances of the script
pkill -f "main.py"

# Killing all instances of Firefox
killall -9 Firefox

# Generate a temporary directory
install_dir="/tmp/blossomandbloom-$(uuidgen)"

# Clone the GitHub repository into the temporary directory
git clone https://github.com/arminius2/BlossomAndBloom.git $install_dir

# Navigate to the project directory
cd $install_dir

# Run pip3 as the current user to install Python dependencies
sudo -u $(logname) pip3 install --user -r dependencies.txt

# Sync the contents of the temporary directory to the user's home directory
rsync -av --delete $install_dir/ $HOME/.blossomandbloom/

# Create LaunchAgents directory if it doesn't exist
launch_agents_dir="$HOME/Library/LaunchAgents"
if [ ! -d "$launch_agents_dir" ]; then
  sudo -u $(logname) mkdir -p "$launch_agents_dir"
fi

# Create Launch Agent plist file
plist_path="$launch_agents_dir/com.blossomandbloom.app.plist"

# Unload existing launch agent if it exists
if [ -f "$plist_path" ]; then
  sudo -u $(logname) launchctl bootout gui/$(id -u $(logname)) "$plist_path"
fi

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
    <string>$HOME/.blossomandbloom/main.py</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>" > $plist_path

# Set ownership and permissions
chmod 644 $plist_path
chown $(logname):$(id -gn $(logname)) $plist_path

# Load the new launch agent
sudo -u $(logname) launchctl bootstrap gui/$(id -u $(logname)) "$plist_path"

# Check if YouTube stream key is set
youtube_key=$(keyring get BlossomAndBloom YouTubeStream)

if [ -z "$youtube_key" ]; then
  echo "No YouTube stream key is set."
  echo -n "Please enter your YouTube stream key: "
  read -r stream_key

  python3 -c "import keyring; keyring.set_password('BlossomAndBloom', 'YouTubeStream', '$stream_key')"
fi

# Change ownership of the entire installation to the non-root user
chown -R $(logname):$(id -gn $(logname)) $HOME/.blossomandbloom

# Remove the temporary directory
rm -rf $install_dir

echo "Installation complete."

# Killing all instances of the script
pkill -f "main.py"

# Killing all instances of Firefox
killall -9 Firefox