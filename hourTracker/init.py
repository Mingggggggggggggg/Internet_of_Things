import DbManager as dbm
import mqttHost as mH
import webServer as wS
import sqlite3

def main():

    con = dbm.initDB()
    #Datensatz aktualisieren
    #dbm.readCsv(con, dbm.csvPath)
    #con.close()
    
    #Starte MQTT Client
    mH.startMqttClient()

    #Starte Webserver
    wS.readFromDatabase(con)
if __name__ == "__main__":
    main()