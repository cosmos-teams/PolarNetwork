#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

// Define UART for AS32 module - using default UART0
#define LORA_SERIAL Serial1
#define LORA_TX_PIN 0    // GP0 - UART0 TX
#define LORA_RX_PIN 1    // GP1 - UART0 RX
#define LORA_M0_PIN 2    // GPIO pin for M0
#define LORA_M1_PIN 3    // GPIO pin for M1
#define LED_PIN 25       // Built-in LED on Pico

Adafruit_BNO055 bno = Adafruit_BNO055(55);

// LoRa parameters
const uint16_t nodeID = 0;     // Address 0
const uint16_t freq = 433;     // 433MHz (matching the example)
const uint8_t power = 22;      // 22dBm

void setup(void) 
{
  pinMode(LORA_M0_PIN, OUTPUT);
  pinMode(LORA_M1_PIN, OUTPUT);
  
  // Set to normal mode: M0=0, M1=0
  digitalWrite(LORA_M0_PIN, LOW);
  digitalWrite(LORA_M1_PIN, LOW);
  
  pinMode(LED_PIN, OUTPUT);
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

void sendMessage(const char* msg) {
    // Calculate frequency offset for 433MHz
    uint8_t offset_frequence = freq - 410;  // For 433MHz band
    
    digitalWrite(LED_PIN, HIGH);
    
    // Format matching the example:
    // [dest_addr_high][dest_addr_low][freq_offset][own_addr_high][own_addr_low][own_freq_offset][payload]
    LORA_SERIAL.write(0xFF);  // Destination high byte (255)
    LORA_SERIAL.write(0xFF);  // Destination low byte (255)
    LORA_SERIAL.write(offset_frequence);
    LORA_SERIAL.write(nodeID >> 8);    // Own address high byte
    LORA_SERIAL.write(nodeID & 0xFF);  // Own address low byte
    LORA_SERIAL.write(offset_frequence);
    LORA_SERIAL.print(msg);
    
    
    delay(100);
    digitalWrite(LED_PIN, LOW);
}

void checkIncomingMessages() {
  while (LORA_SERIAL.available()) {
    Serial.println("\n--- Received LoRa packet ---");
    
    // Read header bytes
    byte sender = LORA_SERIAL.read();
    byte recipient = LORA_SERIAL.read();
    byte length = LORA_SERIAL.read();
    
    Serial.printf("Sender ID: 0x%02X\n", sender);
    Serial.printf("Recipient ID: 0x%02X\n", recipient);
    Serial.printf("Data length: %d\n", length);
    
    // Read payload
    Serial.print("Data (hex): ");
    for (int i = 0; i < length; i++) {
      byte b = LORA_SERIAL.read();
      Serial.printf("0x%02X ", b);
    }
    Serial.println();
    
    // Try to print as ASCII
    LORA_SERIAL.setTimeout(100);  // Reset position to start of payload
    String message = LORA_SERIAL.readString();
    Serial.print("Data (ASCII): ");
    Serial.println(message);
    
    Serial.println("------------------------");
  }
}

void loop(void) 
{
  // Check for incoming messages
  checkIncomingMessages();
  
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
  sendMessage(data.c_str());
  
  // Add small delay to allow receiving
  delay(100);
}