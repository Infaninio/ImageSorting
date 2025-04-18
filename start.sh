#!/bin/bash

# Change directory to WebUI
cd WebUI || { echo "Cannot go into WebUI directory"; exit 1; }

# Infinite loop to restart the Flask app
while true
do
    echo "Starting Flask application..."
    python -m flask run --host=0.0.0.0 --port=5000

    # Optionally, add a small delay before restarting in case of crashes
    echo "Flask app stopped. Restarting in 5 seconds..."
    sleep 5
done
