from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import json
import asyncio
from datetime import datetime
import uvicorn
from pathlib import Path

app = FastAPI()

# Store the latest sensor data
latest_data = {}

# HTML template for the web interface
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>BNO055 Sensor Monitor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
            .card {
                border: 1px solid #ccc;
                padding: 15px;
                border-radius: 8px;
                background: #f8f9fa;
            }
            .value { font-size: 1.2em; font-weight: bold; }
            .timestamp { color: #666; font-size: 0.8em; }
            table { width: 100%; border-collapse: collapse; }
            td { padding: 4px; }
            .cal-0 { background: #ffcdd2; }
            .cal-1 { background: #fff9c4; }
            .cal-2 { background: #c8e6c9; }
            .cal-3 { background: #69f0ae; }
        </style>
    </head>
    <body>
        <h1>BNO055 Sensor Monitor</h1>
        <div class="timestamp">Last Update: <span id="timestamp">-</span></div>
        <div class="container">
            <div class="card">
                <h3>Orientation (deg)</h3>
                <table>
                    <tr><td>X:</td><td id="orientation_x" class="value">-</td></tr>
                    <tr><td>Y:</td><td id="orientation_y" class="value">-</td></tr>
                    <tr><td>Z:</td><td id="orientation_z" class="value">-</td></tr>
                </table>
            </div>
            <div class="card">
                <h3>Accelerometer (m/s²)</h3>
                <table>
                    <tr><td>X:</td><td id="accel_x" class="value">-</td></tr>
                    <tr><td>Y:</td><td id="accel_y" class="value">-</td></tr>
                    <tr><td>Z:</td><td id="accel_z" class="value">-</td></tr>
                </table>
            </div>
            <div class="card">
                <h3>Gyroscope (rad/s)</h3>
                <table>
                    <tr><td>X:</td><td id="gyro_x" class="value">-</td></tr>
                    <tr><td>Y:</td><td id="gyro_y" class="value">-</td></tr>
                    <tr><td>Z:</td><td id="gyro_z" class="value">-</td></tr>
                </table>
            </div>
            <div class="card">
                <h3>Linear Acceleration (m/s²)</h3>
                <table>
                    <tr><td>X:</td><td id="linear_x" class="value">-</td></tr>
                    <tr><td>Y:</td><td id="linear_y" class="value">-</td></tr>
                    <tr><td>Z:</td><td id="linear_z" class="value">-</td></tr>
                </table>
            </div>
            <div class="card">
                <h3>Magnetometer (µT)</h3>
                <table>
                    <tr><td>X:</td><td id="mag_x" class="value">-</td></tr>
                    <tr><td>Y:</td><td id="mag_y" class="value">-</td></tr>
                    <tr><td>Z:</td><td id="mag_z" class="value">-</td></tr>
                </table>
            </div>
            <div class="card">
                <h3>Gravity (m/s²)</h3>
                <table>
                    <tr><td>X:</td><td id="gravity_x" class="value">-</td></tr>
                    <tr><td>Y:</td><td id="gravity_y" class="value">-</td></tr>
                    <tr><td>Z:</td><td id="gravity_z" class="value">-</td></tr>
                </table>
            </div>
            <div class="card">
                <h3>System Status</h3>
                <table>
                    <tr><td>Temperature:</td><td id="temp" class="value">-</td></tr>
                    <tr><td>RSSI:</td><td id="rssi" class="value">-</td></tr>
                </table>
            </div>
            <div class="card">
                <h3>Calibration Status</h3>
                <table>
                    <tr><td>System:</td><td id="cal_sys" class="value">-</td></tr>
                    <tr><td>Gyro:</td><td id="cal_gyro" class="value">-</td></tr>
                    <tr><td>Accel:</td><td id="cal_accel" class="value">-</td></tr>
                    <tr><td>Mag:</td><td id="cal_mag" class="value">-</td></tr>
                </table>
            </div>
        </div>
        <script>
            const ws = new WebSocket("ws://" + window.location.host + "/ws");
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                document.getElementById("timestamp").textContent = new Date().toLocaleTimeString();
                
                // Update all values
                updateVector("orientation", data.orientation);
                updateVector("accel", data.accel);
                updateVector("gyro", data.gyro);
                updateVector("linear", data.linear_accel);
                updateVector("mag", data.mag);
                updateVector("gravity", data.gravity);
                
                // Update temperature and calibration
                document.getElementById("temp").textContent = data.temp + "°C";
                document.getElementById("rssi").textContent = data.rssi || "-";
                
                updateCalibration("cal_sys", data.cal.sys);
                updateCalibration("cal_gyro", data.cal.gyro);
                updateCalibration("cal_accel", data.cal.accel);
                updateCalibration("cal_mag", data.cal.mag);
            };
            
            function updateVector(prefix, vector) {
                if (vector) {
                    document.getElementById(prefix + "_x").textContent = vector.x.toFixed(3);
                    document.getElementById(prefix + "_y").textContent = vector.y.toFixed(3);
                    document.getElementById(prefix + "_z").textContent = vector.z.toFixed(3);
                }
            }
            
            function updateCalibration(id, value) {
                const element = document.getElementById(id);
                element.textContent = value;
                element.className = "value cal-" + value;
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if latest_data:
                await websocket.send_json(latest_data)
            await asyncio.sleep(0.1)  # Send updates every 100ms
    except:
        await websocket.close()

def update_data(data):
    """Update the latest sensor data"""
    global latest_data
    latest_data = data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 