#!/bin/bash
HOME_DIR=$(echo ~)

# Check if the findora-toolbox directory exists and move it to fractal-toolbox
if [ -d "$HOME_DIR/findora-toolbox" ]; then
  mv ~/findora-toolbox ~/fractal-toolbox
fi

if [ -d "$HOME_DIR/.findora.env" ]; then
  mv ~/.findora.env ~/.fractal.env
fi

# Check if the fractal-toolbox directory exists
if [ -d "$HOME_DIR/fractal-toolbox" ]; then
  # If it exists, go into it and pull updates
  cd ~/fractal-toolbox
  git pull --quiet
else
  # If it doesn't exist, clone the repository
  git clone https://github.com/FindoraNetwork/findora-toolbox.git ~/fractal-toolbox
  # Go into the new directory, we already have updates
  cd ~/fractal-toolbox
fi

# Install requirements for both
pip3 install -r requirements.txt --quiet

# Start toolbox, with flags if passed
python3 ~/fractal-toolbox/src/app.py "$@"