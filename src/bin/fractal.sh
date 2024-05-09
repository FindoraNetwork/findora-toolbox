#!/bin/bash
HOME_DIR=$(echo ~)

# Check if the fractal-toolbox directory exists
if [ -d "$HOME_DIR/fractal-toolbox" ]; then
  # If it exists, go into it and pull updates
  cd ~/fractal-toolbox
  git pull --quiet
else
  # If it doesn't exist, clone the repository
  git clone https://github.com/fractalNetwork/fractal-toolbox.git ~/fractal-toolbox
  # Go into the new directory, we already ahve updates
  cd ~/fractal-toolbox
fi

# Install requirements for both
pip3 install -r requirements.txt --quiet

# Start toolbox, with flags if passed
python3 ~/fractal-toolbox/src/app.py "$@"