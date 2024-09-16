#!/bin/bash

# Path to your virtual environment
VENV_PATH="/home/ubuntu/dexter/wakemeup-server/wakemeup"

# Path to your log file
LOG_FILE="/home/ubuntu/dexter/wakemeup-server/logs/script_execution.log"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Run the script every 15 seconds
while true
do
    # Log the start time of the script execution to both log file and terminal
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Running Python script" | tee -a "$LOG_FILE"

    # Run the Python script
    python3 scripts/main.py

    # Wait for 15 seconds
    sleep 15
done
