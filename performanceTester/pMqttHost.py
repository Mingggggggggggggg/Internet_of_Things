import random
import string
import threading
import time
import paho.mqtt.client as mqtt
import json
import sqlite3
import pDbManager as dm
import pInit as init

MQTT_PUB_LATRESPONSE = "/esp32/latencyResponse"
MQTT_SUB_LATMESSAGE = "/esp32/latencyMessage"

totalSend = 100
qos = 0
sleep = 0.1
messageSizeReal = 1024 #1024 für 1kb

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_SUB_LATMESSAGE)

def on_message(client, userdata, message):
    try:
        raw_payload = message.payload.decode("utf-8").strip()
        #print(f"Topic: {message.topic}, Payload: {raw_payload}")

        if message.topic == MQTT_SUB_LATMESSAGE:
            try:
                payload = json.loads(raw_payload)
                datum = payload["datum"]
                timestamp = int(payload["timestamp"]) 
                mqttQos = payload["QoS"]
                message_size = len(message.payload)

                now_ms = int(time.time() * 1000)  
                latency = now_ms - timestamp      

                con = sqlite3.connect(dm.filepath)
                dm.insert(con, datum, mqttQos, latency, message_size)
                con.close()
                #print(f"Eingefügt: {datum}; {latency} ms; QoS {mqttQos}; Größe {message_size}")
                print("", end="")
                print(".", end="", flush=True)

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                #print(f"Topic: {message.topic}, Payload: {raw_payload}")
                print(f"Fehler beim Verarbeiten der Nachricht: {e}")

    except Exception as e:
        print(f"Payload kann nicht dekodiert werden")

def sendMessage(client):
    count = totalSend
    while count > 0:
        random_string = ''.join(random.choices(string.ascii_letters, k=messageSizeReal))
        timestamp = int(time.time() * 1000)
        payload = json.dumps({
            "datum": time.strftime("%Y-%m-%d"),
            "timestamp": timestamp,
            "QoS": qos,
            "message": random_string
        })

        client.publish(MQTT_PUB_LATRESPONSE, payload=payload, qos=qos)
        #print(f"Nachricht gesendet:\n{payload}")
        count -= 1
        time.sleep(sleep)
    if count==0:
        print("Fertig")

def startMqttClient():
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect("localhost", 1883, 60)

    sender_thread = threading.Thread(target=sendMessage, args=(mqttc,))
    sender_thread.daemon = True
    sender_thread.start()

    mqttc.loop_forever()
