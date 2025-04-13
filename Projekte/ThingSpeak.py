import adafruit_dht # import libary

from board import <pin> # import 1-Wire board pin



dht_device = adafruit_dht.DHT22(<pin>) # initialize device
temperature = dht_device.temperature # get temperature
humidity = dht_device.humidity # get humidity