#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi

# Check if the directory exists
if [ ! -d "$HOME/.blossomandbloom" ]; then
    mkdir "$HOME/.blossomandbloom"
fi

# Clone the GitHub repository into ~/.blossomandbloom
git clone https://github.com/arminius2/BlossomAndBloom.git $HOME/.blossomandbloom

# Navigate to the project directory
cd $HOME/.blossomandbloom

# Install Python dependencies
pip3 install -r dependencies.txt

# Add the main script to run at login on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  osascript -e "tell application \"System Events\" to make login item at end with properties {path:\"$HOME/.blossomandbloom/main.py\", hidden:false}"
fi

# Set the sticky bit on install.sh
chmod +t $HOME/.blossomandbloom/install.sh

# Check if YouTube stream key is set
youtube_key=$(keyring get BlossomAndBloom YouTubeStream)

if [ -z "$youtube_key" ]; then
  echo "No YouTube stream key is set."
  echo -n "Please enter your YouTube stream key: "
  read -r stream_key

  python3 -c "import keyring; keyring.set_password('BlossomAndBloom', 'YouTubeStream', '$stream_key')"
fi
