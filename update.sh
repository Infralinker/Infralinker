#!/bin/bash
#
# Script Name: update.sh
# Description: Update script for the Infralinker application.
# Author: Abdellah ALAOUI ISMAILI
# Version: 1.0.1

# Check if the infralinker app and Nginx are running
echo "Checking if the Infralinker app and Nginx are running..."
if systemctl is-active --quiet nginx && systemctl is-active --quiet infralinkerd; then
    echo "nginx & infralinkerd Services are running, please stop them. Exiting..."
    exit 1
fi

echo "Copying config files to a new folder..."

# Define the directory
directory="$HOME/infralinker"

# Check if the infralinker directory exists
if [ -d "$directory" ]; then
    # Check if the migrations folder exists within the infralinker directory
    if [ -d "$directory/migrations" ]; then
        # Copy the migrations folder and configuration files to the current directory
        cp -r "$directory/migrations" . || { echo "Failed to copy migrations folder"; exit 1; }
        cp "$directory/production.ini" . || { echo "Failed to copy production.ini"; exit 1; }
        cp "$directory/wsgi.py" . || { echo "Failed to copy wsgi.py"; exit 1; }
        echo "Files copied successfully."
    else
        echo "Migrations folder does not exist, please install the Infralinker app first."
        exit 1
    fi
else
    echo "Infralinker directory does not exist. Exiting."
    exit 1
fi

echo "Changing the folder for Infralinker app"

# Get the current path
current_path=$(pwd)

# Create or update the symbolic link
ln -snf "$current_path" "$HOME/infralinker" || { echo "Failed to create symbolic link"; exit 1; }

echo "Symbolic link updated successfully."

# Activate the virtual environment
echo "Activating the virtual environment..."
source $HOME/infralinker_venv/bin/activate
source "$directory"/export.sh

# Check for changes in requirements.txt compared to installed packages
echo "Checking for changes in requirements..."
if diff <(sort requirements.txt) <(pip freeze | sort) > /dev/null; then
    echo "No changes in requirements."
else
    echo "Requirements have changed. Updating..."
    pip install -r requirements.txt
fi

# Run flask db migrate commands
echo "Running flask db migrate commands..."
flask db migrate
flask db upgrade

# Deactivate virtual environment
echo "Deactivating the virtual environment..."
deactivate

# Restart app infralinkerd service and Nginx
echo "Restarting app service and Nginx..."
sudo systemctl start infralinkerd
sudo systemctl start nginx

echo "Update completed successfully."
