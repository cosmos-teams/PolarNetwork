from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store the latest sensor data
latest_data = {}

# Simplified HTML template
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Sensor Monitor</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { 
                font-family: Arial; 
                margin: 20px;
                background: #f0f0f0;
            }
            .container { 
                max-width: 800px;
                margin: 0 auto;
            }
            .card {
                background: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .value {
                font-weight: bold;
                color: #2196F3;
            }
            .timestamp {
                color: #666;
                font-size: 0.9em;
                margin-bottom: 20px;
            }
            h2 {
                margin-top: 0;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Sensor Monitor</h1>
            <div class="timestamp">Last Update: <span id="timestamp">-</span></div>
            
            <div class="card">
                <h2>Orientation</h2>
                <div>X: <span id="orientation_x" class="value">-</span>°</div>
                <div>Y: <span id="orientation_y" class="value">-</span>°</div>
                <div>Z: <span id="orientation_z" class="value">-</span>°</div>
            </div>

            <div class="card">
                <h2>Accelerometer</h2>
                <div>X: <span id="accel_x" class="value">-</span> m/s²</div>
                <div>Y: <span id="accel_y" class="value">-</span> m/s²</div>
                <div>Z: <span id="accel_z" class="value">-</span> m/s²</div>
            </div>

            <div class="card">
                <h2>System Status</h2>
                <div>RSSI: <span id="rssi" class="value">-</span></div>
                <div>Calibration: <span id="cal_sys" class="value">-</span></div>
            </div>

            <div class="card">
                <h2>Linear Acceleration</h2>
                <div>X: <span id="linear_accel_x" class="value">-</span> m/s²</div>
                <div>Y: <span id="linear_accel_y" class="value">-</span> m/s²</div>
                <div>Z: <span id="linear_accel_z" class="value">-</span> m/s²</div>
            </div>

            <div class="card">
                <h2>Linear Acceleration Graph</h2>
                <canvas id="linearAccelChart"></canvas>
            </div>
        </div>

        <script>
            // Initialize the chart
            const ctx = document.getElementById('linearAccelChart').getContext('2d');
            const maxDataPoints = 50;
            
            const linearAccelChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'X Linear Acceleration',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        tension: 0.1
                    }, {
                        label: 'Y Linear Acceleration',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }, {
                        label: 'Z Linear Acceleration',
                        data: [],
                        borderColor: 'rgb(153, 102, 255)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: {
                                display: true,
                                text: 'Linear Acceleration (m/s²)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Time'
                            }
                        }
                    }
                }
            });

            function updateData() {
                fetch('/data')
                    .then(response => response.json())
                    .then(data => {
                        const timestamp = new Date().toLocaleTimeString();
                        document.getElementById("timestamp").textContent = timestamp;
                        
                        // Update orientation
                        if (data.orientation) {
                            document.getElementById("orientation_x").textContent = data.orientation.x.toFixed(2);
                            document.getElementById("orientation_y").textContent = data.orientation.y.toFixed(2);
                            document.getElementById("orientation_z").textContent = data.orientation.z.toFixed(2);
                        }
                        
                        // Update accelerometer
                        if (data.accel) {
                            document.getElementById("accel_x").textContent = data.accel.x.toFixed(2);
                            document.getElementById("accel_y").textContent = data.accel.y.toFixed(2);
                            document.getElementById("accel_z").textContent = data.accel.z.toFixed(2);
                        }
                        
                        // Update status
                        document.getElementById("rssi").textContent = data.rssi || "-";
                        document.getElementById("cal_sys").textContent = data.cal ? data.cal.sys : "-";

                        // Update linear acceleration values
                        if (data.linear_accel) {
                            document.getElementById("linear_accel_x").textContent = data.linear_accel.x.toFixed(2);
                            document.getElementById("linear_accel_y").textContent = data.linear_accel.y.toFixed(2);
                            document.getElementById("linear_accel_z").textContent = data.linear_accel.z.toFixed(2);

                            // Update chart
                            linearAccelChart.data.labels.push(timestamp);
                            linearAccelChart.data.datasets[0].data.push(data.linear_accel.x);
                            linearAccelChart.data.datasets[1].data.push(data.linear_accel.y);
                            linearAccelChart.data.datasets[2].data.push(data.linear_accel.z);

                            // Remove old data points if we have too many
                            if (linearAccelChart.data.labels.length > maxDataPoints) {
                                linearAccelChart.data.labels.shift();
                                linearAccelChart.data.datasets.forEach(dataset => dataset.data.shift());
                            }

                            linearAccelChart.update();
                        }
                    })
                    .catch(console.error);
            }

            // Update every second
            setInterval(updateData, 1000);
            updateData();  // Initial update
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.get("/data")
async def get_data():
    return JSONResponse(latest_data)

@app.post("/update")
async def update_data(data: dict):
    global latest_data
    latest_data = data
    return {"status": "ok"}

def run():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)