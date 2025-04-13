import Adafruit_DHT

sensor = Adafruit_DHT.DHT22
pin = 4  # GPIO-Nummer, nicht Pin-Nummer

humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

if humidity is not None and temperature is not None:
    print(f'Temp: {temperature:.1f}°C  Luftfeuchtigkeit: {humidity:.1f}%')
else:
    print('Sensor nicht auslesbar')
