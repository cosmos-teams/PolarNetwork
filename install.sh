#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Check if root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo -e "${GREEN}Starting installation...${NC}"

# Install dependencies
apt-get update && apt-get install -y python3-pip python3-venv python3-dev

# Setup Python environment
python3 -m venv "${SCRIPT_DIR}/venv"
source "${SCRIPT_DIR}/venv/bin/activate"
pip install --upgrade pip wheel
pip install -r "${SCRIPT_DIR}/baseStation/requirements.txt"

# Create service
cat > /etc/systemd/system/lora-monitor.service << EOL
[Unit]
Description=LoRa Sensor Monitor
After=network.target

[Service]
Type=simple
User=$SUDO_USER
Environment=PYTHONPATH=${SCRIPT_DIR}
Environment=PATH=${SCRIPT_DIR}/venv/bin:\$PATH
WorkingDirectory=${SCRIPT_DIR}/baseStation
ExecStart=${SCRIPT_DIR}/venv/bin/python3 ${SCRIPT_DIR}/baseStation/src/baseStation.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Setup permissions and start
chmod 644 /etc/systemd/system/lora-monitor.service
chown $SUDO_USER:$SUDO_USER -R "${SCRIPT_DIR}"
mkdir -p "${SCRIPT_DIR}/baseStation/logs"
chown $SUDO_USER:$SUDO_USER "${SCRIPT_DIR}/baseStation/logs"

systemctl daemon-reload
systemctl enable lora-monitor.service
systemctl start lora-monitor.service

# Create uninstall script
cat > "${SCRIPT_DIR}/uninstall.sh" << EOL
#!/bin/bash
[ "\$EUID" -ne 0 ] && echo "Please run as root" && exit 1
systemctl stop lora-monitor.service
systemctl disable lora-monitor.service
rm /etc/systemd/system/lora-monitor.service
systemctl daemon-reload
rm -rf "${SCRIPT_DIR}/venv"
echo "Uninstalled"
EOL
chmod +x "${SCRIPT_DIR}/uninstall.sh"

# Final status
if systemctl is-active --quiet lora-monitor.service; then
    echo -e "${GREEN}Installation successful! Service is running.${NC}"
    echo -e "Web interface: http://localhost:8000"
    echo -e "View logs: sudo journalctl -u lora-monitor.service -f"
else
    echo -e "${RED}Service failed to start. Check logs with: journalctl -u lora-monitor.service -f${NC}"
fi 