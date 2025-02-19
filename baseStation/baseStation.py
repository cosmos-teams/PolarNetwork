#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sx126x
import json
import time
import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime
import csv
import os

# Data storage for plotting
class DataBuffer:
    def __init__(self, max_points=100):
        self.max_points = max_points
        self.times = []
        self.x_vals = []
        self.y_vals = []
        self.z_vals = []
        
        # Initialize plot
        plt.ion()  # Enable interactive mode
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.lines = [
            self.ax.plot([], [], label='X')[0],
            self.ax.plot([], [], label='Y')[0],
            self.ax.plot([], [], label='Z')[0]
        ]
        self.ax.set_title('Orientation Data')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Degrees')
        self.ax.legend()
        self.ax.grid(True)

    def update(self, x, y, z):
        current_time = datetime.datetime.now()
        self.times.append(current_time)
        self.x_vals.append(x)
        self.y_vals.append(y)
        self.z_vals.append(z)
        
        # Keep only max_points
        if len(self.times) > self.max_points:
            self.times = self.times[-self.max_points:]
            self.x_vals = self.x_vals[-self.max_points:]
            self.y_vals = self.y_vals[-self.max_points:]
            self.z_vals = self.z_vals[-self.max_points:]
        
        # Update plot
        time_numbers = [(t - self.times[0]).total_seconds() for t in self.times]
        self.lines[0].set_data(time_numbers, self.x_vals)
        self.lines[1].set_data(time_numbers, self.y_vals)
        self.lines[2].set_data(time_numbers, self.z_vals)
        
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

# Initialize data buffer and CSV logging
data_buffer = DataBuffer()
log_filename = f"sensor_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
os.makedirs('logs', exist_ok=True)
log_path = os.path.join('logs', log_filename)

# Create CSV file with headers
with open(log_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Timestamp', 'X', 'Y', 'Z', 'RSSI'])

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
        # Convert bytes to string
        data_str = data[3:-1].decode('utf-8')
        
        # Find the start of JSON data (first '{')
        json_start = data_str.find('{')
        if json_start == -1:
            raise ValueError("No JSON object found in data")
            
        # Extract just the JSON portion
        json_str = data_str[json_start:]
        
        # Parse JSON data
        sensor_data = json.loads(json_str)
        
        # Update plot and log data
        x, y, z = sensor_data['x'], sensor_data['y'], sensor_data['z']
        data_buffer.update(x, y, z)
        
        # Log to CSV
        timestamp = datetime.datetime.now().isoformat()
        rssi = f"-{256-data[-1:][0]}dBm" if node.rssi else "N/A"
        with open(log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, x, y, z, rssi])
        
        # Print formatted sensor readings
        print("Sensor Readings:")
        print(f"X: {x:.4f}")
        print(f"Y: {y:.4f}")
        print(f"Z: {z:.4f}")
        
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON data: {e}")
        print(f"Raw data: {data_str}")
    except Exception as e:
        print(f"Error processing data: {e}")

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