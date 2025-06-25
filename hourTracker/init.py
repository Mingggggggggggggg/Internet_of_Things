import DbManager as dm
import mqttHost as mH
import webServer as wS
import threading

def main():
    #initDB nimmt boolean als Parameter an. Ist es auf true gesetzt, dann wird die Datenbank
    #neu erstellt und mit dem Grundbestand befüllt. Ist diese auf false gesetzt, wird bloß con wiedergegeben.
    #Existiert keine Datenbank, dann wird eine neue erstellt und mit dem Grundbestand befüllt.
    dm.initDB(False)

    mqtt_thread = threading.Thread(target=mH.startMqttClient, daemon=True)
    mqtt_thread.start()

    wS.startServer() 

if __name__ == "__main__":
    main()