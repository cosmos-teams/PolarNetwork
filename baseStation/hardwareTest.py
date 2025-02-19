import serial
import time
import os
import stat
import json

def check_port_access(port_path):
    try:
        # Check if file exists
        if not os.path.exists(port_path):
            print(f"Error: {port_path} does not exist")
            return False
            
        # Check permissions
        mode = os.stat(port_path).st_mode
        print(f"Port permissions: {stat.filemode(mode)}")
        print(f"Current user: {os.getuid()}")
        print(f"Current groups: {os.getgroups()}")
        
        return True
    except Exception as e:
        print(f"Error checking port access: {e}")
        return False

def test_serial_port():
    port_path = '/dev/ttyACM0'
    
    print("\n--- Port Access Check ---")
    if not check_port_access(port_path):
        return
        
    print("\n--- Serial Port Test ---")
    try:
        print(f"Attempting to open {port_path}...")
        ser = serial.Serial(
            port=port_path,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        
        print("Serial port opened successfully")
        print(f"Port settings: {ser.get_settings()}")
        
        # Send configuration query
        print("\nSending configuration query...")
        ser.write(bytes([0xC1, 0x00, 0x09]))
        time.sleep(0.5)
        
        # Read response
        if ser.in_waiting:
            response = ser.read(ser.in_waiting)
            print(f"Raw response: {[hex(x) for x in response]}")
        else:
            print("No response received")
        
        ser.close()
        print("Port closed successfully")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

def parse_sensor_data(data):
    try:
        # Convert bytes to string
        data_str = data[3:-1].decode('utf-8')
        
        # Remove "Sent: " prefix if present
        if data_str.startswith("Sent: "):
            data_str = data_str.replace("Sent: ", "")
        
        # Remove any trailing whitespace or newlines
        data_str = data_str.strip()
        
        # Parse JSON data
        sensor_data = json.loads(data_str)
        
        # Print formatted sensor readings
        print("Sensor Readings:")
        print(f"X: {sensor_data['x']:.4f}")
        print(f"Y: {sensor_data['y']:.4f}")
        print(f"Z: {sensor_data['z']:.4f}")
        
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse JSON data: {e}")
        print(f"Raw data: {data_str}")
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    test_serial_port()