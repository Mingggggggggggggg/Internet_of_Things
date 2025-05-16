import datetime
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
        raw_payload = message.payload.decode().strip()
        print(f"Topic: {message.topic}, Payload: {raw_payload}")
        
        if message.topic == MQTT_PUB_HOURS:
            try:
                payload = json.loads(raw_payload)
                stunden = float(str(payload["stunden"]).replace(",", "."))
                stunden = round(stunden, 1)
                datum = payload["datum"]
            except json.JSONDecodeError:
                stunden = float(raw_payload.replace(",", "."))
                stunden = round(stunden, 1)
                datum = datetime.datetime.now().strftime("%Y-%m-%d")
                print("Fallback")
            

            con = sqlite3.connect(dbm.filepath)
            dbm.insert(con, datum, stunden)
            con.close()
            print(f"Eingefügt: {datum} ; {stunden}h")
            
    except Exception as e:
        print(f"Fehler: {str(e)}")



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
