#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sx126x
import json
import time

# Initialize LoRa module
# Using 868MHz frequency, address 0xFF (base station), 22dBm power, with RSSI enabled
node = sx126x.sx126x(
    serial_num="/dev/ttyAMA0",  # Serial port for Ubuntu on RPi
    freq=868,                   # Frequency in MHz
    addr=0xFF,                  # Base station address
    power=22,                   # Power in dBm
    rssi=True,                  # Enable RSSI reading
    air_speed=2400              # Air speed (bps)
)

def parse_sensor_data(data):
    try:
        # Extract the payload from the received data
        # Skip the header bytes (sender, recipient, length)
        payload = data[3:-1].decode('utf-8')
        
        # Parse JSON data
        sensor_data = json.loads(payload)
        
        # Print formatted sensor readings
        print("Sensor Readings:")
        print(f"X: {sensor_data['x']:.4f}")
        print(f"Y: {sensor_data['y']:.4f}")
        print(f"Z: {sensor_data['z']:.4f}")
        
    except json.JSONDecodeError:
        print("Error: Could not parse JSON data")
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