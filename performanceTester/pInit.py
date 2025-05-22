import pDbManager as dm
import pMqttHost as mH

def main():

    dm.initDB()

    mH.startMqttClient()


if __name__ == "__main__":
    main()
