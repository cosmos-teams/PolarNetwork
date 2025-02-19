#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

// Define UART for AS32 module - using default UART0
#define LORA_SERIAL Serial1
#define LORA_TX_PIN 0  // GP0 - UART0 TX
#define LORA_RX_PIN 1  // GP1 - UART0 RX

Adafruit_BNO055 bno = Adafruit_BNO055(55);

// LoRa parameters
const byte nodeID = 0x02;      // This device's ID
const byte baseStation = 0xFF;  // Destination ID (base station)

void setup(void) 
{
  Serial.begin(9600);
  LORA_SERIAL.begin(9600);
  
  Serial.println("Orientation Sensor Test");
  
  if(!bno.begin()) {
    Serial.print("No BNO055 detected!");
    while(1);
  }
  
  delay(1000);
  bno.setExtCrystalUse(true);
}

void sendLoRaPacket(String data) {
  // Format: [sender][recipient][length][data]
  LORA_SERIAL.write(nodeID);          // Sender ID
  LORA_SERIAL.write(baseStation);     // Recipient ID
  LORA_SERIAL.write(data.length());   // Package length
  LORA_SERIAL.print(data);            // Data
}

void loop(void) 
{
  // Read all sensor data
  sensors_event_t orientationData, angVelocityData, linearAccelData, magnetometerData, 
                 accelerometerData, gravityData;
  
  bno.getEvent(&orientationData, Adafruit_BNO055::VECTOR_EULER);
  bno.getEvent(&angVelocityData, Adafruit_BNO055::VECTOR_GYROSCOPE);
  bno.getEvent(&linearAccelData, Adafruit_BNO055::VECTOR_LINEARACCEL);
  bno.getEvent(&magnetometerData, Adafruit_BNO055::VECTOR_MAGNETOMETER);
  bno.getEvent(&accelerometerData, Adafruit_BNO055::VECTOR_ACCELEROMETER);
  bno.getEvent(&gravityData, Adafruit_BNO055::VECTOR_GRAVITY);

  // Get temperature
  int8_t temp = bno.getTemp();

  // Get calibration status
  uint8_t system, gyro, accel, mag = 0;
  bno.getCalibration(&system, &gyro, &accel, &mag);
  
  // Format data as JSON string
  String data = "{\"orientation\":{" 
                "\"x\":" + String(orientationData.orientation.x, 4) + 
                ",\"y\":" + String(orientationData.orientation.y, 4) + 
                ",\"z\":" + String(orientationData.orientation.z, 4) + "},"
                "\"gyro\":{" 
                "\"x\":" + String(angVelocityData.gyro.x, 4) + 
                ",\"y\":" + String(angVelocityData.gyro.y, 4) + 
                ",\"z\":" + String(angVelocityData.gyro.z, 4) + "},"
                "\"accel\":{" 
                "\"x\":" + String(accelerometerData.acceleration.x, 4) + 
                ",\"y\":" + String(accelerometerData.acceleration.y, 4) + 
                ",\"z\":" + String(accelerometerData.acceleration.z, 4) + "},"
                "\"linear_accel\":{" 
                "\"x\":" + String(linearAccelData.acceleration.x, 4) + 
                ",\"y\":" + String(linearAccelData.acceleration.y, 4) + 
                ",\"z\":" + String(linearAccelData.acceleration.z, 4) + "},"
                "\"gravity\":{" 
                "\"x\":" + String(gravityData.acceleration.x, 4) + 
                ",\"y\":" + String(gravityData.acceleration.y, 4) + 
                ",\"z\":" + String(gravityData.acceleration.z, 4) + "},"
                "\"mag\":{" 
                "\"x\":" + String(magnetometerData.magnetic.x, 4) + 
                ",\"y\":" + String(magnetometerData.magnetic.y, 4) + 
                ",\"z\":" + String(magnetometerData.magnetic.z, 4) + "},"
                "\"temp\":" + String(temp) + ","
                "\"cal\":{" 
                "\"sys\":" + String(system) + 
                ",\"gyro\":" + String(gyro) + 
                ",\"accel\":" + String(accel) + 
                ",\"mag\":" + String(mag) + "}}";
  
  // Send data over LoRa
  sendLoRaPacket(data);
  
  delay(1000);  // 1Hz sampling rate
}