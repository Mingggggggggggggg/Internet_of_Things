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

const char* ssid = WIFI_SSID;
const char* password = WIFI_PASS;