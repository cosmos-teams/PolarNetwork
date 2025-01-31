#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>
#include "bleinfo.h"

BLECharacteristic *characteristicMessage;
const size_t bufferSize = JSON_OBJECT_SIZE(20);

byte baseStation = 0xFF;
byte nodeID = 0x01;
byte syncWord = 0x14;

#define nss 2
#define rst 19
#define dio0 17

class MyServerCallbacks : public BLEServerCallbacks
{
  void onConnect(BLEServer *server)
  {
    Serial.println("Connected");
  };

  void onDisconnect(BLEServer *server)
  {
    Serial.println("Disconnected");
    server->startAdvertising(); // start advertising again
  }
};

class MessageCallbacks : public BLECharacteristicCallbacks
{
  void onWrite(BLECharacteristic *characteristic)
  {
    std::string data = characteristic->getValue();
    Serial.println(data.c_str());
  }

  void onRead(BLECharacteristic *characteristic)
  {
    characteristic->setValue("Foobar");
  }
};

void sendJsonOverBluetooth(int sender, int recipient, String packet, float snr, int rssi, long freqErr)
{
  StaticJsonDocument<bufferSize> jsonDoc;
  jsonDoc["sender"] = sender;
  jsonDoc["recipient"] = recipient;
  jsonDoc["message"] = packet;
  jsonDoc["SNR"] = snr;
  jsonDoc["RSSI"] = rssi;
  jsonDoc["FreqErr"] = freqErr;

  // Serialize the JSON object to a string
  String jsonString;
  serializeJson(jsonDoc, jsonString);

  // Print the JSON string to the Serial monitor
  // Serial.println(jsonString);

  // Update the BLE characteristic value
  characteristicMessage->setValue(jsonString.c_str());

  // Notify connected devices about the updated value
  characteristicMessage->notify();
}

void onReceive(int packetSize)
{
  if (packetSize == 0)
    return;

  byte sender = LoRa.read();
  int recipient = LoRa.read();
  byte packageLength = LoRa.read();

  float snr = LoRa.packetSnr();
  int rssi = LoRa.packetRssi();
  long freqErr = LoRa.packetFrequencyError();

  String packet = "";

  while (LoRa.available())
  {
    packet += (char)LoRa.read();
  }

  if (packageLength != packet.length())
  {
    Serial.println("error: message length does not match length");
    return;
  }

  if (recipient != nodeID && recipient != baseStation)
  {
    Serial.println("This message is not for me.");
    return;
  }

  String message = String(sender) + " -> " + recipient + " : " + packet;

  message += " | SNR: " + String(snr) + " | RSSI: " + String(rssi) + " | FreqErr: " + String(freqErr);
  Serial.println(message);
  // Serial.println(packet);

  sendJsonOverBluetooth(sender, recipient, packet, snr, rssi, freqErr);
  packet = "";
}

void setup()
{
  delay(2000);
  Serial.begin(115200);
  LoRa.setPins(nss, rst, dio0);

  if (!LoRa.begin(433E6))
  {
    Serial.println("LoRa init failed. Check your connections.");
    while (true)
      ;
  }

  LoRa.setSyncWord(syncWord);
  // LoRa.setSpreadingFactor(10);
  LoRa.setGain(6);

  Serial.println("LoRa init succeeded.");

  // Setup BLE Server
  BLEDevice::init(DEVICE_NAME);
  BLEServer *server = BLEDevice::createServer();
  server->setCallbacks(new MyServerCallbacks());

  // Register message service that can receive messages and reply with a static message.
  BLEService *service = server->createService(SERVICE_UUID);
  characteristicMessage = service->createCharacteristic(MESSAGE_UUID, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_WRITE);
  characteristicMessage->setCallbacks(new MessageCallbacks());
  characteristicMessage->addDescriptor(new BLE2902());
  service->start();

  // Register device info service, that contains the device's UUID, manufacturer and name.
  service = server->createService(DEVINFO_UUID);
  BLECharacteristic *characteristic = service->createCharacteristic(DEVINFO_MANUFACTURER_UUID, BLECharacteristic::PROPERTY_READ);
  characteristic->setValue(DEVICE_MANUFACTURER);
  characteristic = service->createCharacteristic(DEVINFO_NAME_UUID, BLECharacteristic::PROPERTY_READ);
  characteristic->setValue(DEVICE_NAME);
  characteristic = service->createCharacteristic(DEVINFO_SERIAL_UUID, BLECharacteristic::PROPERTY_READ);
  String chipId = String((uint32_t)(ESP.getEfuseMac() >> 24), HEX);
  characteristic->setValue(chipId.c_str());
  service->start();

  // Advertise services
  BLEAdvertising *advertisement = server->getAdvertising();
  BLEAdvertisementData adv;
  adv.setName(DEVICE_NAME);
  adv.setCompleteServices(BLEUUID(SERVICE_UUID));
  advertisement->setAdvertisementData(adv);
  advertisement->start();

  Serial.println("Ready");

  Serial.println("Bluetooth initialized.");
}

void loop()
{
  onReceive(LoRa.parsePacket());
}