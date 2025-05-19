import pDbManager as dm
import pMqttHost as mH
#import pWebServer as wS
#import threading

def main():

    dm.initDB()

    # Threade MqttClient, um ungewollte Latenzen zu vermeiden
    #mqtt_thread = threading.Thread(target=mH.startMqttClient, daemon=True)
    #mqtt_thread.start()

    mH.startMqttClient()


    #Deaktiviere webServer, um Overhead zu reduzieren. Visualisierungen werden manuell angelegt
    #wS.startServer() 

if __name__ == "__main__":
    main()
