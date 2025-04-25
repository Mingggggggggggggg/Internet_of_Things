import threading
import time
from flask import Flask, render_template
import DB_Manager as dbm
import gpiozero as GPIO

app = Flask(__name__)

def measureTrigger():
    while True:
        dbm.measure()
        time.sleep(10)

@app.route("/")
def main():
    readings = dbm.read_from_database()
    return render_template("main.html", readings=readings)

if __name__ == "__main__":
    print("DHT22 Sensor - Temperatur und Luftfeuchtigkeit")
    measureThread = threading.Thread(target=measureTrigger, daemon=True)
    measureThread.start()

    try:
        app.run(host='localhost', port=8181, debug=True)
    except KeyboardInterrupt:
        GPIO.cleanup()
