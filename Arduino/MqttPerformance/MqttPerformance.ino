#include <Arduino.h>
#include <WiFi.h>
#include "../keys.h"
extern "C" {
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"
}
#include <AsyncMqttClient.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <NTPClient.h>

#define MQTT_HOST IPAddress(192, 168, 178, 124)
#define MQTT_PORT 1883


#define MQTT_PUB_LATSEND "/esp32/latencySend"
#define MQTT_SUB_LATREC "/esp32/latencyReceive"
#define MQTT_PUB_LATRES "/esp32/latencyResult"

uint8_t qualityOfService = 0;
uint64_t timestampMil = 0;


TimerHandle_t mqttReconnectTimer;
TimerHandle_t wifiReconnectTimer;
AsyncMqttClient mqttClient;

// Internet Uhr
WiFiUDP ntpUDP;
// Passe an auf GMT+1
NTPClient timeClient(ntpUDP, "pool.ntp.org", 3600, 60000);



void connectToWifi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
}

void connectToMqtt() {
  Serial.println("Connecting to MQTT...");
  mqttClient.connect();
}

void onWiFiEvent(WiFiEvent_t event) {
  Serial.printf("[WiFi-event] event: %d\n", event);
  switch (event) {
    case ARDUINO_EVENT_WIFI_STA_GOT_IP:
      Serial.println("WiFi connected");
      Serial.println("IP address: ");
      Serial.println(WiFi.localIP());
      connectToMqtt();
      break;
    case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
      Serial.println("WiFi lost connection");
      xTimerStop(mqttReconnectTimer, 0);
      xTimerStart(wifiReconnectTimer, 0);
      break;
  }
}

void onMqttConnect(bool sessionPresent) {
  Serial.println("Connected to MQTT.");
  Serial.print("Session present: ");
  Serial.println(sessionPresent);
}

void onMqttDisconnect(AsyncMqttClientDisconnectReason reason) {
  Serial.println("Disconnected from MQTT.");
  if (WiFi.isConnected()) {
    xTimerStart(mqttReconnectTimer, 0);
  }
}

void onMqttPublish(uint16_t packetId) {
  Serial.print("Publish acknowledged.");
  Serial.print(" packetId: ");
  Serial.println(packetId);
}

String getCurrentDate() {
  timeClient.update();
  time_t epochTime = timeClient.getEpochTime();
  struct tm* ptm = gmtime(&epochTime);

  char dateBuffer[11];
  sprintf(dateBuffer, "%04d-%02d-%02d", ptm->tm_year + 1900, ptm->tm_mon + 1, ptm->tm_mday);
  return String(dateBuffer);
}

void syncClock() {
  timeClient.update();
  Serial.println("NTP-Zeit synchronisiert.");
}

void sendData() {
  if (WiFi.status() != WL_CONNECTED || !mqttClient.connected()) {
    Serial.println("Keine WiFi/MQTT-Verbindung!");
    return;
  }
  timestampMil = esp_timer_get_time();

  DynamicJsonDocument doc(128);
  doc["datum"] = getCurrentDate();
  doc["timestamp"] = timestampMil;
  doc["qos"] = qualityOfService;
  doc["message"] = "test";

  String payload;
  serializeJson(doc, payload);

  mqttClient.publish(MQTT_PUB_LATSEND, qualityOfService, false, payload.c_str());
  Serial.println(timestampMil);
  Serial.println(qualityOfService);
  Serial.println("Gesendet");
}

void onMqttMessage(char* topic, char* payload, AsyncMqttClientMessageProperties properties,
                   size_t len, size_t index, size_t total) {
  if (strcmp(topic, MQTT_SUB_LATREC) != 0) return;  // Korrektes Topic prüfen

  uint64_t now = esp_timer_get_time();

  DynamicJsonDocument doc(128);
  DeserializationError error = deserializeJson(doc, payload);
  if (error) {
    Serial.print("JSON-Fehler: ");
    Serial.println(error.c_str());
    return;
  }

  uint64_t sent = doc["timestamp"];
  uint64_t latency = now - sent;

  DynamicJsonDocument result(128);
  result["datum"] = getCurrentDate();
  result["qos"] = qualityOfService;
  result["latency"] = latency;
  result["size"] = strlen(payload);

  String resultPayload;
  serializeJson(result, resultPayload);

  mqttClient.publish(MQTT_PUB_LATRES, 0, false, resultPayload.c_str());  // korrektes Topic
  Serial.printf("Latenz: %llu µs\n", latency);
}


void setup() {
  Serial.begin(115200);

  mqttReconnectTimer = xTimerCreate("mqttTimer", pdMS_TO_TICKS(2000),
                                    pdFALSE, (void*)0, reinterpret_cast<TimerCallbackFunction_t>(connectToMqtt));
  wifiReconnectTimer = xTimerCreate("wifiTimer", pdMS_TO_TICKS(2000),
                                    pdFALSE, (void*)0, reinterpret_cast<TimerCallbackFunction_t>(connectToWifi));

  WiFi.onEvent(onWiFiEvent);

  mqttClient.onConnect(onMqttConnect);
  mqttClient.onDisconnect(onMqttDisconnect);
  mqttClient.onPublish(onMqttPublish);
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);

  mqttClient.onMessage(onMqttMessage);
  mqttClient.subscribe(MQTT_SUB_LATREC, qualityOfService);

  connectToWifi();

  timeClient.begin();
  syncClock();
}
static unsigned long lastSent = 0;
void loop() {
  if (millis() - lastSent > 5000 && mqttClient.connected()) {
    sendData();
    lastSent = millis();
  }
}