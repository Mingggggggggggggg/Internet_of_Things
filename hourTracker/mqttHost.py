import paho.mqtt.client as mqtt
import json
import DbManager as dbm

MQTT_PUB_HOURS = "/esp32/Lost_Ark/hours"
SQLITE_DB_PATH = "dataset.db"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_PUB_HOURS)



# TODO TRY CATCH BLOCK um die Fehlerhaften bztw üngültige Daten des DHT22 auszusortieren.
def on_message(client, userdata, message):
    try: 
        print("MQTT message received")
        if message.topic == MQTT_PUB_HOURS:
            print("DHT readings update")
        
        dbm.insert()
    except Exception as e:
        print(f" Error: {str(e)}")