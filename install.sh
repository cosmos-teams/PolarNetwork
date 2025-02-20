#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    echo -e "${2}${1}${NC}"
}

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then 
    print_message "Please run as root (use sudo)" "$RED"
    exit 1
fi

# Get the actual path of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

print_message "Starting installation..." "$GREEN"

# Update system
print_message "Updating system packages..." "$YELLOW"
apt-get update
apt-get upgrade -y

# Install required system packages
print_message "Installing required system packages..." "$YELLOW"
apt-get install -y python3-pip python3-venv git

# Create virtual environment
print_message "Setting up Python virtual environment..." "$YELLOW"
python3 -m venv "${SCRIPT_DIR}/venv"
source "${SCRIPT_DIR}/venv/bin/activate"

# Install Python requirements
print_message "Installing Python requirements..." "$YELLOW"
pip install -r "${SCRIPT_DIR}/baseStation/requirements.txt"

# Create systemd service file
print_message "Creating systemd service..." "$YELLOW"
cat > /etc/systemd/system/lora-monitor.service << EOL
[Unit]
Description=LoRa Sensor Monitor
After=network.target

[Service]
Type=simple
User=$SUDO_USER
Environment=PYTHONPATH=${SCRIPT_DIR}/venv/lib/python3.9/site-packages
WorkingDirectory=${SCRIPT_DIR}/baseStation
ExecStart=${SCRIPT_DIR}/venv/bin/python3 ${SCRIPT_DIR}/baseStation/src/baseStation.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Set correct permissions
print_message "Setting permissions..." "$YELLOW"
chmod 644 /etc/systemd/system/lora-monitor.service
chown $SUDO_USER:$SUDO_USER -R "${SCRIPT_DIR}"

# Create logs directory with correct permissions
mkdir -p "${SCRIPT_DIR}/baseStation/logs"
chown $SUDO_USER:$SUDO_USER "${SCRIPT_DIR}/baseStation/logs"

# Enable and start service
print_message "Enabling and starting service..." "$YELLOW"
systemctl daemon-reload
systemctl enable lora-monitor.service
systemctl start lora-monitor.service

# Check if service is running
if systemctl is-active --quiet lora-monitor.service; then
    print_message "Installation completed successfully!" "$GREEN"
    print_message "The service is now running." "$GREEN"
    print_message "\nUseful commands:" "$YELLOW"
    print_message "- Check service status: sudo systemctl status lora-monitor.service" "$NC"
    print_message "- View logs: sudo journalctl -u lora-monitor.service -f" "$NC"
    print_message "- Restart service: sudo systemctl restart lora-monitor.service" "$NC"
    print_message "- Web interface: http://localhost:8000" "$NC"
else
    print_message "Installation completed but service failed to start." "$RED"
    print_message "Please check the logs: sudo journalctl -u lora-monitor.service -f" "$RED"
fi

# Create uninstall script
print_message "Creating uninstall script..." "$YELLOW"
cat > "${SCRIPT_DIR}/uninstall.sh" << EOL
#!/bin/bash
if [ "\$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Stop and disable service
systemctl stop lora-monitor.service
systemctl disable lora-monitor.service
rm /etc/systemd/system/lora-monitor.service
systemctl daemon-reload

# Remove virtual environment
rm -rf "${SCRIPT_DIR}/venv"

echo "Uninstallation completed"
EOL

chmod +x "${SCRIPT_DIR}/uninstall.sh"

print_message "\nAn uninstall script has been created. To remove everything, run: sudo ./uninstall.sh" "$YELLOW" 