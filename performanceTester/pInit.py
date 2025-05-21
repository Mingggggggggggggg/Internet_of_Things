import pDbManager as dm
import pMqttHost as mH

def main():
    #initDB nimmt boolean als Parameter an. Ist es auf true gesetzt, dann wird die Datenbank
    #neu erstellt und mit dem Grundbestand befüllt. Ist diese auf false gesetzt, wird bloß con wiedergegeben
    dm.initDB(false)

    #Starte MQTTClient
    mH.startMqttClient()


if __name__ == "__main__":
    main()
