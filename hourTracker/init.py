import DbManager as dbm

if __name__ == "__main__":
    con = dbm.initDB()
    dbm.readCsv(con, dbm.CSV_PATH)
    con.close()