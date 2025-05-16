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

#define MQTT_HOST IPAddress(192, 168, 178, 124)
#define MQTT_PORT 1883
#define MQTT_PUB_HOURS "/esp32/Lost_Ark/hours"
#define LOST_ARK_APPID 1599340

// Timer-Handler
TimerHandle_t mqttReconnectTimer;
TimerHandle_t wifiReconnectTimer;

// MQTT-Client
AsyncMqttClient mqttClient;

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

void getHours() {
  if (WiFi.status() != WL_CONNECTED || !mqttClient.connected()) {
    Serial.println("Keine WiFi/MQTT-Verbindung!");
    return;
  }
// https://developer.valvesoftware.com/wiki/Steam_Web_API#GetRecentlyPlayedGames_(v0001)
  HTTPClient http;
  String url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/";
  url += "?key=" + String(STEAM_API_KEY);
  url += "&steamid=" + String(TARGET_STEAM_ID);
  url += "&format=json";
  url += "&include_played_free_games=1";

  http.begin(url);
  int httpCode = http.GET();

  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();
    DynamicJsonDocument doc(2048);
    DeserializationError error = deserializeJson(doc, payload);

    if (error) {
      Serial.print("JSON Deserialization failed: ");
      Serial.println(error.c_str());
      http.end();
      return;
    }

    if (doc["response"].containsKey("games")) {
      JsonArray games = doc["response"]["games"];
      for (JsonObject game : games) {
        if (game["appid"] == LOST_ARK_APPID) {
          int playtimeMinutes = game["playtime_forever"];
          float playtimeHours = playtimeMinutes / 60.0f;

          char mqttPayload[20];
          snprintf(mqttPayload, sizeof(mqttPayload), "%.1f", playtimeHours);
          mqttClient.publish(MQTT_PUB_HOURS, 1, true, mqttPayload);

          Serial.printf("Lost Ark Spielstunden: %.1f h\n", playtimeHours);
          break;
        }
      }
    } else {
      Serial.println("Keine Spiele gefunden oder Profil privat!");
    }
  } else {
    Serial.printf("HTTP-Fehler: %d\n", httpCode);
  }
  http.end();
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

  connectToWifi();
}

void loop() {
  static unsigned long lastUpdate = 0;
  const unsigned long interval = 300000; // 5 Minuten (Steam API Ratelimit)

  if (millis() - lastUpdate >= interval) {
    getHours();
    lastUpdate = millis();
  }
}