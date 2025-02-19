#!/bin/bash

# Create the service file
sudo tee /etc/systemd/system/bno055-monitor.service << EOF
[Unit]
Description=BNO055 Sensor Monitor
After=network.target

[Service]
ExecStart=/usr/bin/python3 $(pwd)/baseStation.py
WorkingDirectory=$(pwd)
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