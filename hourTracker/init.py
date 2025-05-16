import DbManager as dbm
import mqttHost as mH

if __name__ == "__main__":
    con = dbm.initDB()
    dbm.readCsv(con, dbm.csvPath)
    con.close()