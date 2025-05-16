import sqlite3
import os

filepath = "./performance.db"


# Übernommen aus Laborübung 12
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d



# Übernommen aus Laborübung 12 connect:with()   
# Stelle eine Verbindung zur Datenbank her, existiert keine Datenbank, wird diese erstellt und gefüllt               
def initDB():
    if not os.path.exists(filepath):
        con = sqlite3.connect(filepath)
        con.row_factory = dict_factory
        with con:
            cur = con.cursor()
            cur.execute("""
            DROP TABLE IF EXISTS performanceTable
            """)
            cur.execute("""
            CREATE TABLE performanceTable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                qos INTEGER,
                latency INTEGER,
                message INTEGER
            )
            """)
            con.commit()
    else:
        con = sqlite3.connect(filepath)
        con.row_factory = dict_factory
    return con


# Methode zum Einfügen von Daten in die Datenbank
def insert(con, timestamp, qos, latency, message):
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO performanceTable (timestamp, qos, latency, message) VALUES (?, ?, ?, ?)", (timestamp, qos, latency, message))

# Methode zum abrufen der absoluten Stunden für den Webserver
def getAllData():
    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute("SELECT timestamp, qos, latency, message FROM performanceTable ORDER BY datum ASC")
    data = cur.fetchall()
    con.close()
    return data

# Methide zum abrufen der relativen Studnen für den Webserver
def getRelativeData():
    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute("SELECT datum, relativeStunden FROM performanceTable ORDER BY datum ASC")
    data = cur.fetchall()
    con.close()
    return data