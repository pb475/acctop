#!/bin/bash

echo "=============================="
echo "Building the acctop command"
echo "=============================="

# Print out command arguments during execution
set -x

# Remove the venv if it exists
echo "=============================="
echo "Removing the venv if it exists"
if [ -d "venv" ]; then
    rm -rf venv
fi

# Install the required packages
echo "=============================="
echo "Installing the required packages"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install --upgrade pip
pip install --upgrade pip
pip install -r requirements.txt

# Create the executable using PyInstaller
echo "=============================="
echo "Creating the executable using PyInstaller"
pyinstaller --onefile acctop.py

# Check if the directory exists before creating it
echo "=============================="
echo "Creating the .bin directory in the home directory"
if [ ! -d "$HOME/.bin/" ]; then
    mkdir "$HOME/.bin/"
fi

# Remove the previous version of acctop if it exists
echo "=============================="
echo "Removing the previous version of acctop if it exists"
if [ -f "$HOME/.bin/acctop" ]; then
    rm "$HOME/.bin/acctop"
fi

# Move the new version of acctop to the .bin directory
echo "=============================="
echo "Moving the new version of acctop to the .bin directory"
mv dist/acctop "$HOME/.bin/acctop"

# Add .bin directory to PATH in shell configuration files (bashrc and zshrc for common ones)
echo "=============================="
echo "Adding .bin directory to PATH in shell configuration files"
for shell_config in "$HOME/.bashrc" "$HOME/.zshrc"; do
    echo "Adding .bin directory to PATH in $shell_config"
    if [ -f "$shell_config" ]; then
        echo 'export PATH="$PATH:$HOME/.bin"' >> "$shell_config"
        source "$shell_config"
    fi
done



# Clean up the build directory
echo "=============================="
echo "Cleaning up the build directory"
rm -rf build/ dist/ __pycache__/ acctop.spec

echo "================================================================"
echo "Build process completed"
echo "to use: try the command acctop from anywhere on the command line"
echo "================================================================"