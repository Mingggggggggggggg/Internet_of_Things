from datetime import datetime
import sqlite3
import time
import adafruit_dht
import board

dht_device = adafruit_dht.DHT22(board.D4, use_pulseio=False)

connection = sqlite3.connect("dht22.db")

cursor = connection.cursor()
cursor.execute("SELECT SQLITE_VERSION()")

def measure():
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        now = datetime.now()
        currentdate = now.strftime("%Y-%m-%d")
        currenttime = now.strftime("%H:%M:%S")
        print(f"Temperatur: {temperature} Feuchtigkeit: {humidity} \n Datum: {currentdate} Zeit: {currenttime}")
        toDB(temperature, humidity, currentdate, currenttime)


    except RuntimeError as e:
        print(f"Sensorfehler: {e}")
        
    except KeyboardInterrupt:
        dht_device.exit()



def toDB(temperature, humidity, currentdate, currenttime):
    cursor.execute("INSERT INTO dhtreadings (temperature, humidity, currentdate, currentime) VALUES(?, ?, ?, ?)", (temperature, humidity, currentdate, currenttime))
    connection.commit()


if __name__ == "__main__":
    try:
        while(True):
            measure()
            time.sleep(5)
    except KeyboardInterrupt:
        dht_device.exit()