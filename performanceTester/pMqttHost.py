import datetime
import paho.mqtt.client as mqtt
import json
import sqlite3
import pDbManager as dm

MQTT_PUB_LATSEND = "/esp32/latencySend"
MQTT_SUB_LATREC = "/esp32/latencyReceive"
MQTT_PUB_LATRES = "/esp32/latencyResult"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_PUB_LATSEND)

# Übernommen aus Laborübung 12
# Bei Ankunft der Nachricht bereinige die Json und und schicke an den DbManager zum einfügen
def onLatencyMessage(client, userdata, message):
    try:
        raw_payload = message.payload.decode("utf-8").strip()
        print(f"Topic: {message.topic}, Payload: {raw_payload}")

        if message.topic == MQTT_PUB_LATSEND:
            try:
                payload = json.loads(raw_payload)
                datum = payload["datum"]
                timestamp = int(payload["timestamp"])
                qos = short(payload["qos"])


                print(f"Eingefügt: {datum} ; {stunden} h")

                # Echo für den ESP32 senden (für RTT-Berechnung)
                client.publish(MQTT_SUB_LATREC, raw_payload)

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Fehler beim Verarbeiten der Nachricht: {e}")

    except Exception as e:
        print(f"Allg. Fehler: {e}")

def onLatencyResult(client, userdata, message):
    try:
        raw_payload = message.payload.decode("utf-8").strip()
        print(f"Topic: {message.topic}, Payload: {raw_payload}")

        if message.topic == MQTT_PUB_LATRES:
            try:
                payload = json.loads(raw_payload)
                datum = payload["datum"]
                timestamp = int(payload["timestamp"])
                qos = short(payload["qos"])


                print(f"Eingefügt: {datum} ; {stunden} h")

                # Echo für den ESP32 senden (für RTT-Berechnung)
                client.publish(MQTT_SUB_LATREC, raw_payload)

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Fehler beim Verarbeiten der Nachricht: {e}")

    except Exception as e:
        print(f"Allg. Fehler: {e}")

# Übernommen aus Laborübung 12
def startMqttClient():
    try:
        mqttc = mqtt.Client()
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        mqttc.connect("localhost", 1883, 60)
        mqttc.loop_forever()
        print("Client gestartet")
    except KeyboardInterrupt:
        print("Beendet durch Benutzer.")