import datetime
import pDbManager as dm
import pMqttHost as mH
import pWebServer as wS
import threading

def main():
    #Zum aktualisieren des Datensatzes folgende Zeile auskommentieren
    con = dm.initDB()

    mqtt_thread = threading.Thread(target=mH.startMqttClient, daemon=True)
    mqtt_thread.start()

    wS.startServer() 

if __name__ == "__main__":
    #main()

    time = datetime.time()
    print(time)