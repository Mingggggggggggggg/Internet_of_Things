import pDbManager as dm
import pMqttHost as mH
import pWebServer as wS
import threading

def main():

    dm.initDB()

    mqtt_thread = threading.Thread(target=mH.startMqttClient, daemon=True)
    mqtt_thread.start()

    wS.startServer() 

if __name__ == "__main__":
    main()
