import time
import os
import board
import json
import adafruit_dht
import thingspeak
from dotenv import load_dotenv

# Initial the dht device, with data pin connected to:
load_dotenv()
dht_device = adafruit_dht.DHT22(board.D4, use_pulseio=False)

WRITE_KEY = os.getenv("TS_W_KEY")
READ_KEY = os.getenv("TS_R_KEY")

def measure(channel:thingspeak.Channel):
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        channel.api_key = WRITE_KEY
        params = {
            "api_key" : "",
            "field1" : temperature,
            "field2" : humidity
        }
        channel.update(params)
        channel.api_key = READ_KEY
        field1_data = json.loads(channel.get_field_last(field=1))
        field2_data = json.loads(channel.get_field_last(field=2))
        field1 = field1_data["field1"]
        field2 = field2_data["field2"]
        print(f"Temperatur: {field1} humidity: {field2}")


    except RuntimeError as e:
        print(f"Sensorfehler: {e}")
        
    except KeyboardInterrupt:
        dht_device.exit()


if __name__ == "__main__":
    channel = thingspeak.Channel(os.getenv("TS_CHANNEL"))
    try:
        while(True):
            measure(channel)
            time.sleep(5)
    except KeyboardInterrupt:
        dht_device.exit()