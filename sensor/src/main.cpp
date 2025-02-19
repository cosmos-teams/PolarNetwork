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
  
  if(!bno.begin())
  {
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
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
  sensors_event_t event; 
  bno.getEvent(&event);
  
  // Format data as JSON string
  String data = "{\"x\":" + String(event.orientation.x, 4) + 
                ",\"y\":" + String(event.orientation.y, 4) + 
                ",\"z\":" + String(event.orientation.z, 4) + "}";
  
  // Send data over LoRa
  sendLoRaPacket(data);
  
  delay(1000);
}