#!/bin/bash
HOME_DIR=$(echo ~)

# Check if the findora-toolbox directory exists
if [ -d "$HOME_DIR/findora-toolbox" ]; then
  # If it exists, go into it and pull updates
  cd ~/findora-toolbox
  git pull --quiet
else
  # If it doesn't exist, clone the repository
  git clone https://github.com/FindoraNetwork/findora-toolbox.git ~/findora-toolbox
  # Go into the new directory, we already ahve updates
  cd ~/findora-toolbox
fi

# Install requirements for both
pip3 install -r requirements.txt --quiet

# Start toolbox, with flags if passed
python3 ~/findora-toolbox/src/app.py "$@"