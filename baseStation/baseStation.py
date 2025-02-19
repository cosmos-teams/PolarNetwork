#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sx126x
import json
import time
import sys

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