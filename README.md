# LoRa Sensor Base Station

This project implements a base station for receiving and monitoring LoRa sensor data. It includes a web interface for real-time data visualization.

## Technology Stack

### Backend
- **Python 3.9+**: Core programming language
- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: Lightning-fast ASGI server
- **Pydantic**: Data validation using Python type annotations

### Hardware Interface
- **SX126X**: LoRa module interface library
- **PySerial**: Serial port communication

### Frontend
- **HTML/CSS**: Basic web interface
- **JavaScript**: Real-time data updates
- **Chart.js**: Data visualization
- **WebSocket**: Real-time communication

### System
- **Systemd**: Service management
- **Python venv**: Virtual environment for dependency isolation

## Requirements

- Raspberry Pi (or similar Linux-based system)
- Python 3.9 or higher
- LoRa module connected via serial port
- Internet connection for initial setup

## Installation

1. Clone this repository:

```bash
git clone https://github.com/cosmos-teams/PolarNetwork.git
cd PolarNetwork
```

2. Run the installation script:

```bash
sudo ./install.sh
```

The installation script will:
- Update system packages
- Install required dependencies
- Create a Python virtual environment
- Set up the system service
- Configure permissions

## Usage

After installation, the base station service will start automatically and run on system boot.

### Web Interface
Access the web interface by navigating to:

```bash
http://localhost:8000
```


### Service Management

Check service status:

```bash
sudo systemctl status lora-monitor.service
```

View logs:

```bash
sudo journalctl -u lora-monitor.service -f
```

Restart service:

```bash
sudo systemctl restart lora-monitor.service
```

## Troubleshooting

1. If the service fails to start, check the logs:

```bash
sudo journalctl -u lora-monitor.service -f
```

2. If the web interface is not accessible:
   - Verify the service is running
   - Check your firewall settings
   - Ensure port 8000 is accessible

3. For LoRa communication issues:
   - Check the serial port connection
   - Verify the LoRa module configuration
   - Ensure proper permissions for the serial port
