import adafruit_dht
import board
import time

# DHT22-Sensor an GPIO4 (board.D4)
dht_device = adafruit_dht.DHT22(board.D4)

# Kurze Pause, damit der Sensor bereit ist
time.sleep(2)

try:
    temperature = dht_device.temperature
    humidity = dht_device.humidity

    print(f"Temperatur: {temperature:.1f} C")
    print(f"Luftfeuchtigkeit: {humidity:.1f}%")

except RuntimeError as error:
    print(f"Fehler beim Auslesen: {error}")

finally:
    dht_device.exit()  
