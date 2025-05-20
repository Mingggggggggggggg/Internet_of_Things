import DbManager as dm
import mqttHost as mH
import webServer as wS
import threading

def main():
    #Zum aktualisieren des Datensatzes folgende Zeile auskommentieren, dataset.db löschen und ggf. Pfad in DbManager ergänzen
    #con = dm.initDB()

    mqtt_thread = threading.Thread(target=mH.startMqttClient, daemon=True)
    mqtt_thread.start()

    wS.startServer() 

if __name__ == "__main__":
    main()