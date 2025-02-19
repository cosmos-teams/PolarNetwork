#!/bin/bash

# Get absolute paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_PATH="$SCRIPT_DIR/venv"

# Install python3-venv if not already installed
sudo apt install python3-venv

# Create a virtual environment in the project directory
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install required packages
pip install fastapi uvicorn requests RPi.GPIO pyserial

# Save requirements
pip freeze > requirements.txt

# Create the service file
sudo tee /etc/systemd/system/bno055-monitor.service << EOF
[Unit]
Description=BNO055 Sensor Monitor
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
Environment="PATH=$VENV_PATH/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=$VENV_PATH/lib/python3.*/site-packages:$SCRIPT_DIR"
Environment="PYTHONUNBUFFERED=1"
WorkingDirectory=$SCRIPT_DIR/src
ExecStart=$VENV_PATH/bin/python3 $SCRIPT_DIR/src/baseStation.py
Restart=always
RestartSec=5
StandardOutput=append:/var/log/bno055-monitor.log
StandardError=append:/var/log/bno055-monitor.error.log

[Install]
WantedBy=multi-user.target
EOF

# Create log files and set permissions
sudo touch /var/log/bno055-monitor.log /var/log/bno055-monitor.error.log
sudo chown $USER:$USER /var/log/bno055-monitor.log /var/log/bno055-monitor.error.log

# Make the service file executable
sudo chmod 644 /etc/systemd/system/bno055-monitor.service

# Reload systemd
sudo systemctl daemon-reload

# Stop the service if it's running
sudo systemctl stop bno055-monitor.service

# Enable the service to start on boot
sudo systemctl enable bno055-monitor.service

# Start the service now
sudo systemctl start bno055-monitor.service

# Check status
sudo systemctl status bno055-monitor.service

# Print the paths for verification
echo "Script directory: $SCRIPT_DIR"
echo "Virtual environment: $VENV_PATH"
echo "Log files:"
echo "  - /var/log/bno055-monitor.log"
echo "  - /var/log/bno055-monitor.error.log"

# Print instructions
echo -e "\nTo view logs:"
echo "tail -f /var/log/bno055-monitor.log"
echo "tail -f /var/log/bno055-monitor.error.log" 