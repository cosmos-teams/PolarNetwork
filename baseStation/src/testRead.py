#!/usr/bin/python
# -*- coding: UTF-8 -*-

import serial
import time

# Open serial port
ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

print("Waiting for data... Press Ctrl+C to exit")

try:
    while True:
        if ser.in_waiting:
            # Read all available bytes
            data = ser.read(ser.in_waiting)
            print("Raw data received:", [hex(x) for x in data])
            try:
                print("As string:", data.decode('utf-8'))
            except:
                print("Could not decode as UTF-8")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    ser.close()