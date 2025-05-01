#include "DHT.h"

#define DHTPIN 4

#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  Serial.println("DHT-22 - Temperatur und Luftfeuchtigkeitssensor: ");

  dht.begin();
}

void loop() {
  delay(5000);
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  if (isnan(h) || isnan(t)) {
    Serial.println("Fehler beim Auslesen des Sensors");
    return;
  }
  Serial.println("______________________________________________________");
  Serial.println("Luftfeuchtigkeit: ");
  Serial.print(h);
  Serial.print(" %\t");
  Serial.print("Temperatur: ");
  Serial.print(t);
  Serial.println(" \xe2\x84\x83"); // UTF Code for Grad Celsius
  Serial.println("______________________________________________________");
    Serial.println("  ");
}