import datetime
import threading
import time
import paho.mqtt.client as mqtt
import json
import sqlite3
import pDbManager as dm


MQTT_PUB_LATRESPONSE = "/esp32/latencyResponse"
MQTT_SUB_LATMESSAGE = "/esp32/latencyMessage"

totalSend = 5
qos = 0
# Übernommen aus Laborübung 12
# Bei Verbindungsaufbau abonniere Lost Ark hours vom ESP
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_SUB_LATMESSAGE)

# Angepasst aus https://www.emqx.com/en/blog/how-to-use-mqtt-in-python
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
                message = payload["message"]

            except json.JSONDecodeError:
                print("JSON konnte nicht verarbeitet werden")
            

            con = sqlite3.connect(dm.filepath)
            dm.tempTable(con)  
            dm.insert(con, datum, timestamp, mqttQos, message)
            con.close()
            print(f"Eingefügt: {datum}; {timestamp}; {mqttQos}; {message}")
            
    except Exception as e:
        print(e)

# Angepasst aus https://www.emqx.com/en/blog/how-to-use-mqtt-in-python
def sendMessage(client):
    count = totalSend
    while totalSend < 0:
        timestamp = time.time_ns()
        payload = json.dumps({
            "datum": time.strftime("%Y-%m-%d"),
            "timestamp": timestamp,
            "QoS": qos,
            "message": "test"
        })

        client.publish(MQTT_PUB_LATSEND, qos, payload)
        print("Nachricht gesendet.")
        count -= 1



            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Fehler beim Verarbeiten der Nachricht: {e}")

    except Exception as e:
        print(f"Allg. Fehler: {e}")

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