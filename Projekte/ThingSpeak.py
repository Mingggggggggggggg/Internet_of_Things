import time
import board
import adafruit_dht

# DHT22 an GPIO17 (Pin 11)
dht_device = adafruit_dht.DHT11(board.D4)

try:
    while True:
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            print(f"Temp: {temperature:.1f}�C  Luftfeuchte: {humidity:.1f}%")
        except RuntimeError as e:
            # DHT22 liefert gelegentlich Lesefehler ? ignorieren und neu versuchen
            print(f"Lesefehler: {e.args[0]}")
        time.sleep(2)

except KeyboardInterrupt:
    print("Messung beendet.")

finally:
    dht_device.exit()
