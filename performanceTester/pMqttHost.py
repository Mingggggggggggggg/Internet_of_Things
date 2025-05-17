import datetime
import threading
import time
import paho.mqtt.client as mqtt
import json
import sqlite3
import pDbManager as dm

MQTT_PUB_LATSEND = "/esp32/latencySend"
MQTT_SUB_LATMESSAGE = "/esp32/latencyMessage"

totalSend = 5
qos = 0

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_SUB_LATMESSAGE)

def on_message(client, userdata, message):
    try:
        raw_payload = message.payload.decode("utf-8").strip()
        print(f"Topic: {message.topic}, Payload: {raw_payload}")

        if message.topic == MQTT_SUB_LATMESSAGE:
            try:
                payload = json.loads(raw_payload)
                datum = payload["datum"]
                timestamp = payload["timestamp"]
                mqttQos = payload["QoS"]
                message_text = payload["message"]

                con = sqlite3.connect(dm.filepath)
                dm.tempTable(con)  
                dm.insert(con, datum, timestamp, mqttQos, message_text)
                con.close()
                print(f"Eingefügt: {datum}; {timestamp}; {mqttQos}; {message_text}")

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Fehler beim Verarbeiten der Nachricht: {e}")

    except Exception as e:
        print(f"Payload kann nicht dekodiert werden")

def sendMessage(client):
    count = totalSend
    while count > 0:
        timestamp = time.time_ns()
        payload = json.dumps({
            "datum": time.strftime("%Y-%m-%d"),
            "timestamp": timestamp,
            "QoS": qos,
            "message": "test"
        })

        client.publish(MQTT_PUB_LATSEND, payload=payload, qos=qos)
        print("Nachricht gesendet.")
        count -= 1
        time.sleep(5) 

def startMqttClient():
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect("localhost", 1883, 60)

    sender_thread = threading.Thread(target=sendMessage, args=(mqttc,))
    sender_thread.daemon = True
    sender_thread.start()

    mqttc.loop_forever()

if __name__ == "__main__":
    try:
        startMqttClient()
    except KeyboardInterrupt:
        print("Beendet durch Benutzer.")
