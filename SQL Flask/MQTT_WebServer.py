import paho.mqtt.client as mqtt
import sqlite3
import flask
import json
import sys
import os

MQTT_PUB_TEMP = "/esp32/dht22/temperature"
MQTT_PUB_HUM = "/esp32/dht22/humidity"
MQTT_PUB_READINGS = "/esp32/dht22/readings"
SQLITE_DB_PATH = "./sensordata.db"

app = flask.Flask(__name__)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_PUB_READINGS)
    client.subscribe(MQTT_PUB_TEMP)
    client.subscribe(MQTT_PUB_HUM)


def on_message(client, userdata, message):
    try: 
        print("MQTT message received")
        if message.topic == MQTT_PUB_READINGS:
            print("DHT readings update")
        
        dhtreadings_json = json.loads(message.payload)
        print(dhtreadings_json['temperature'])
        print(dhtreadings_json['humidity'])

        conn=connect_with(SQLITE_DB_PATH)
        c=conn.cursor()
        c.execute("""INSERT INTO dhtreadings (temperature,
            humidity, currentdate, currenttime, device) VALUES((?), (?), date('now'),
            time('now'), (?))""", (dhtreadings_json['temperature'],
            dhtreadings_json['humidity'], 'esp32') )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f" Error: {str(e)}")

def connect_with(filepath):
    con = None
    if not os.path.exists(filepath):
        con = sqlite3.connect(filepath)
        con.row_factory = dict_factory
        with con:
            cursor = con.cursor()
            cursor.execute("""
            DROP TABLE IF EXISTS dhtreadings
            """)
            cursor.execute("""
            CREATE TABLE dhtreadings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature NUMERIC,
                humidity NUMERIC,
                currentdate DATE,
                currenttime DATE,
                device TEXT);
            """)
            con.commit()
    else:
        con = sqlite3.connect(filepath)
        con.row_factory = dict_factory
    return con

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

@app.route("/")
def main():
    readings = read_from_database()
    return flask.render_template('main1.html', readings=readings)

if __name__ == "__main__":
    print('DHT22 Sensor - Temperatur und Luftfeuchtigkeit')
    try:
        mqttc=mqtt.Client()
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        mqttc.connect("localhost",1883,60)
        mqttc.loop_start()
        #mqttc.loop_forever()
        app.run(host='0.0.0.0', port=8181, debug=False)
    except KeyboardInterrupt:
        pass