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

echo "======================================================================"
echo "Partial build process completed"
echo "acctop executable can be found in the dist directory"
echo "You will need to do one of the following:"
echo " - add dist directory to your PATH"
echo " - run it directly from the dist directory, e.g. ./dist/acctop"
echo " - move the executable to a directory in your PATH e.g. /usr/local/bin"
echo "   but usually this requises root permissions"
echo "======================================================================"