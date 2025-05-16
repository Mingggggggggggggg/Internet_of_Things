import paho.mqtt.client as mqtt
import json
import sqlite3
import DbManager as dbm

MQTT_PUB_HOURS = "/esp32/Lost_Ark/hours"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_PUB_HOURS)

def on_message(client, userdata, message):
    try:
        print("MQTT message received")
        if message.topic == MQTT_PUB_HOURS:
            payload = json.loads(message.payload.decode())
            datum = payload["datum"]
            stunden = float(payload["stunden"])

            con = sqlite3.connect(dbm.FILEPATH)
            dbm.insert(con, datum, stunden)
            con.close()
            print(f"Eingefügt: {datum} – {stunden}h")
    except Exception as e:
        print(f"Fehler beim Verarbeiten der Nachricht: {str(e)}")

if __name__ == "__main__":
    print("Starte MQTT Client...")
    try:
        mqttc = mqtt.Client()
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        mqttc.connect("localhost", 1883, 60)
        mqttc.loop_forever()
    except KeyboardInterrupt:
        print("Beendet durch Benutzer.")
