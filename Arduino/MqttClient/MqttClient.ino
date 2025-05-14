#include <Arduino.h>
#include <WiFi.h>
#include "../keys.h"
extern "C" {
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"
}
#include <AsyncMqttClient.h>
#include "DHT.h"


#define DHTPIN 4

#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

//const char* mqtt_login = MQTT_USERNAME;
//const char* mqtt_password = MQTT_PASSWORD;
#define MQTT_HOST IPAddress(192, 168, 178, 124)
#define MQTT_PORT 1883

#define MQTT_PUB_TEMP "/esp32/dht22/temperature"
#define MQTT_PUB_HUM "/esp32/dht22/humidity"
#define MQTT_PUB_READINGS "/esp32/dht22/readings"

AsyncMqttClient mqttClient;
TimerHandle_t mqttReconnectTimer;
TimerHandle_t wifiReconnectTimer;

const int LED_PIN = 2;
char data[80];

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
      xTimerStop(mqttReconnectTimer, 0);  // Nicht gleichzeitig mit MQTT und WiFi wiederverbinden
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

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  dht.begin();
  mqttReconnectTimer = xTimerCreate("mqttTimer", pdMS_TO_TICKS(2000),
                                    pdFALSE, (void*)0, reinterpret_cast<TimerCallbackFunction_t>(connectToMqtt));
  wifiReconnectTimer = xTimerCreate("wifiTimer", pdMS_TO_TICKS(2000),
                                    pdFALSE, (void*)0, reinterpret_cast<TimerCallbackFunction_t>(connectToWifi));
  WiFi.onEvent(onWiFiEvent);
  mqttClient.onConnect(onMqttConnect);
  mqttClient.onDisconnect(onMqttDisconnect);
  mqttClient.onPublish(onMqttPublish);
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);
  // Falls der MQTT-Broker Authentifizierung erzwingt:
  //mqttClient.setCredentials(mqtt_login, mqtt_password);
  connectToWifi();
}

void loop() {
  // 10 Sekunden Pause zwischen den Messungen
  delay(10000);
  // Luftfeuchtigkeit wird gemessen
  float hum = dht.readHumidity();
  // Temperatur wird gemessen
  float temp = dht.readTemperature();
  // Hier wird überprüft, ob die Messungen fehlerfrei druchgelaufen sind
  // Bei Detektion eines Fehlers, wird hier eine Fehelrmeldung ausgegeben
  if (isnan(hum) || isnan(temp)) {
    Serial.println("Fehler beim Auslesen des Sensors");
    return;
  }
  uint16_t packetIdPub1 = mqttClient.publish(MQTT_PUB_TEMP, 1, true, String(temp).c_str());

  Serial.printf("Publishing on topic %s at QoS 1, packetId: %i", MQTT_PUB_TEMP, packetIdPub1);
  Serial.printf("Message: %.2f \n", temp);

  uint16_t packetIdPub2 = mqttClient.publish(MQTT_PUB_HUM, 1, true, String(hum).c_str());

  Serial.printf("Publishing on topic %s at QoS 1, packetId %i: ", MQTT_PUB_HUM, packetIdPub2);
  Serial.printf("Message: %.2f \n", hum);

  String dhtReadings = "{ \"temperature\": \"" + String(temp) + "\", \"humidity\" : \"" + String(hum) + "\"}";
  dhtReadings.toCharArray(data, (dhtReadings.length() + 1));
  uint16_t packetIdPub3 = mqttClient.publish(MQTT_PUB_READINGS, 1, true, String(data).c_str());
  Serial.printf("Publishing on topic %s at QoS 1, packetId %i: ", MQTT_PUB_READINGS, packetIdPub3);

  Serial.printf("Message: %.2f \n", data);
  digitalWrite(LED_PIN, HIGH);
  delay(1000);
  digitalWrite(LED_PIN, LOW);
  delay(1000);
}