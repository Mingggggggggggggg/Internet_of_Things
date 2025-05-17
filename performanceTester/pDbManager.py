import sqlite3
import os

filepath = "./performance.db"



def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d



       
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
                datum DATE,
                timestamp BIGINT,
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



def insert(con, datum, timestamp, qos, latency, message):
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO performanceTable (datum, timestamp, qos, latency, message) VALUES (?, ?, ?, ?)", (datum, timestamp, qos, latency, message))


def getAllData():
    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute("SELECT datum, timestamp, qos, latency, message FROM performanceTable ORDER BY datum ASC")
    data = cur.fetchall()
    con.close()
    return data


def getRelativeData():
    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute("SELECT datum, relativeStunden FROM performanceTable ORDER BY datum ASC")
    data = cur.fetchall()
    con.close()
    return data