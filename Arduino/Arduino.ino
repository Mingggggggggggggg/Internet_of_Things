#include <WiFi.h>
#include "./keys.h"



void setup() {
  Serial.begin(115200);
  WiFi.begin(SSID, PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }


}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\nVerbunden mit WLAN!");
  }
  delay(1000);
}
