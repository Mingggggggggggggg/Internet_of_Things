import paho.mqtt.client as mqtt
import json
import DbManager as dbm

MQTT_PUB_HOURS = "/esp32/Lost_Ark/hours"
SQLITE_DB_PATH = "dataset.db"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_PUB_HOURS)

def connectDB():
    con = dbm.initDB()
    
    pass

def read_from_database():
    con = connect_with(SQLITE_DB_PATH)
    with con:
        cursor = con.cursor()
        cursor.execute("""
        SELECT * FROM dhtreadings
        ORDER BY id DESC LIMIT 20
        """)
        readings = cursor.fetchall()
        print(readings)
        return readings
    return None


def on_message(client, userdata, message):
    try: 
        print("MQTT message received")
        if message.topic == MQTT_PUB_HOURS:
            print("DHT readings update")
        
        dbm.insert()
    except Exception as e:
        print(f" Error: {str(e)}")

if __name__ == "__main__":
    print('DHT22 Sensor - Temperatur und Luftfeuchtigkeit')
    try:
        mqttc=mqtt.Client()
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        mqttc.connect("localhost",1883,60)
        mqttc.loop_start()
    except KeyboardInterrupt:
        pass