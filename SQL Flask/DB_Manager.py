from datetime import datetime
import sqlite3

def measure():
    import adafruit_dht
    import board

    dht_device = adafruit_dht.DHT22(board.D4, use_pulseio=False)

    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        now = datetime.now()
        currentdate = now.strftime("%Y-%m-%d")
        currenttime = now.strftime("%H:%M:%S")

        print(now)
        print(f"Temperatur: {temperature} °C, Feuchtigkeit: {humidity} %, Datum: {currentdate}, Zeit: {currenttime}")

        saveToDB(temperature, humidity, currentdate, currenttime)

    except RuntimeError as e:
        print(f"Sensorfehler: {e}")

    except KeyboardInterrupt:
        dht_device.exit()


def saveToDB(temperature, humidity, currentdate, currenttime):
    con = sqlite3.connect("dht22.db")
    cur = con.cursor()
    cur.execute("""
        INSERT INTO dhtreadings (temperature, humidity, currentdate, currentime)
        VALUES (?, ?, ?, ?)
    """, (temperature, humidity, currentdate, currenttime))
    con.commit()
    con.close()


def read_from_database():
    con = sqlite3.connect("dht22.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM dhtreadings ORDER BY id DESC LIMIT 100")
    daten = cur.fetchall()
    con.close()
    return daten
