#include <WiFi.h>
#include "keys.h"



void setup() {
  Serial.begin(115200);
  WiFi.begin(SSID, PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nVerbunden mit WLAN!");
}

void loop() {
  if (WiFi.status() == true) {
    Serial.print("Verbunden");
  }
  delay(1000);
}
