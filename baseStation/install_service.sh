#!/bin/bash

# Get absolute paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_PATH=$(which python | rev | cut -d'/' -f3- | rev)

# Create the service file
sudo tee /etc/systemd/system/bno055-monitor.service << EOF
[Unit]
Description=BNO055 Sensor Monitor
After=network.target

[Service]
Environment="PATH=$VENV_PATH/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=$VENV_PATH/lib/python3.*/site-packages"
ExecStart=$VENV_PATH/bin/python3 $SCRIPT_DIR/baseStation.py
WorkingDirectory=$SCRIPT_DIR
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

# Make the service file executable
sudo chmod 644 /etc/systemd/system/bno055-monitor.service

# Reload systemd
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable bno055-monitor.service

# Start the service now
sudo systemctl start bno055-monitor.service

# Check status
sudo systemctl status bno055-monitor.service

# Print the paths for verification
echo "Script directory: $SCRIPT_DIR"
echo "Virtual environment: $VENV_PATH" 