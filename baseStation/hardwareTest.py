import serial
import time
import os
import stat

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

if __name__ == "__main__":
    test_serial_port()