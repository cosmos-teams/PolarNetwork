#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sx126x
import json
import time
import sys
import datetime
import csv
import os
import requests
from threading import Thread

# Initialize data buffer and CSV logging
log_filename = f"sensor_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
os.makedirs('logs', exist_ok=True)
log_path = os.path.join('logs', log_filename)

# Create CSV file with headers
with open(log_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Timestamp',
        'Orient_X', 'Orient_Y', 'Orient_Z',
        'Gyro_X', 'Gyro_Y', 'Gyro_Z',
        'Accel_X', 'Accel_Y', 'Accel_Z',
        'Mag_X', 'Mag_Y', 'Mag_Z',
        'Cal_Sys', 'Cal_Gyro', 'Cal_Accel', 'Cal_Mag',
        'RSSI'
    ])

# Initialize LoRa module with error handling
try:
    node = sx126x.sx126x(
        serial_num="/dev/ttyACM0",
        freq=868,
        addr=0xFF,
        power=22,
        rssi=True,
        air_speed=2400
    )
    
    # Verify the serial connection
    if not node.ser.is_open:
        raise Exception("Failed to open serial port")
        
    # Try to write test data
    node.ser.write(bytes([0xC1, 0x00, 0x09]))
    time.sleep(0.1)
    
    if node.ser.in_waiting > 0:
        response = node.ser.read(node.ser.in_waiting)
        print("Module response:", [hex(x) for x in response])
    else:
        print("Warning: No response from module")

except Exception as e:
    print(f"Failed to initialize LoRa module: {e}")
    print("Please check:")
    print("1. Serial port permissions (run 'ls -l /dev/ttyACM0')")
    print("2. Hardware connections (M0, M1, TX, RX)")
    print("3. UART configuration in /boot/firmware/config.txt")
    sys.exit(1)

def parse_sensor_data(data):
    try:
        data_str = data[3:-1].decode('utf-8')
        json_start = data_str.find('{')
        if json_start == -1:
            raise ValueError("No JSON object found in data")
            
        json_str = data_str[json_start:]
        sensor_data = json.loads(json_str)
        
        # Add RSSI to sensor data
        sensor_data['rssi'] = f"-{256-data[-1:][0]}dBm" if node.rssi else "N/A"
        
        # Get current timestamp
        timestamp = datetime.datetime.now().isoformat()
        
        # Log to CSV
        csv_data = [
            timestamp,
            # Orientation
            sensor_data['orientation']['x'],
            sensor_data['orientation']['y'],
            sensor_data['orientation']['z'],
            # Gyroscope
            sensor_data['gyro']['x'],
            sensor_data['gyro']['y'],
            sensor_data['gyro']['z'],
            # Accelerometer
            sensor_data['accel']['x'],
            sensor_data['accel']['y'],
            sensor_data['accel']['z'],
            # Magnetometer
            sensor_data['mag']['x'],
            sensor_data['mag']['y'],
            sensor_data['mag']['z'],
            # Calibration
            sensor_data['cal']['sys'],
            sensor_data['cal']['gyro'],
            sensor_data['cal']['accel'],
            sensor_data['cal']['mag'],
            # RSSI
            sensor_data['rssi']
        ]
        
        with open(log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_data)
        
        # Send to web server
        try:
            requests.post('http://localhost:8000/update', json=sensor_data, timeout=0.1)
        except requests.exceptions.RequestException:
            pass  # Ignore if web server is not running
        
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON data: {e}")
    except Exception as e:
        print(f"Error processing data: {e}")

# Start web server in a separate thread
def run_web_server():
    import web_server
    web_server.run()

Thread(target=run_web_server, daemon=True).start()

try:
    print("LoRa Receiver Started. Press Ctrl+C to exit.")
    
    while True:
        # Check if there's data available to read
        if node.ser.inWaiting() > 0:
            time.sleep(0.1)  # Wait for complete message
            r_buff = node.ser.read(node.ser.inWaiting())
            
            # Print raw data for debugging
            print("\nReceived packet:")
            print(f"Sender ID: {r_buff[0]}")
            print(f"Recipient ID: {r_buff[1]}")
            print(f"Package Length: {r_buff[2]}")
            
            # Parse and display sensor data
            parse_sensor_data(r_buff)
            
            # Print RSSI if enabled
            if node.rssi:
                print(f"RSSI: -{256-r_buff[-1:][0]}dBm")
            
            print("-" * 40)
        
        time.sleep(0.1)  # Small delay to prevent CPU overload

except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Clean up GPIO (if needed)
    node.ser.close()