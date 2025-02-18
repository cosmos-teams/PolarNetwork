import serial
import time

# Try different port names
ports_to_try = ['/dev/ttyAMA0', '/dev/ttyS0', '/dev/serial0']

for port in ports_to_try:
    try:
        print(f"Trying port: {port}")
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=1
        )
        print(f"Successfully opened {port}")
        
        # Try to read configuration
        ser.write(bytes([0xC1, 0x00, 0x09]))
        time.sleep(0.1)
        
        if ser.in_waiting:
            response = ser.read(ser.in_waiting)
            print(f"Response received: {[hex(x) for x in response]}")
        else:
            print("No response received")
            
        ser.close()
        
    except Exception as e:
        print(f"Failed to open {port}: {e}")