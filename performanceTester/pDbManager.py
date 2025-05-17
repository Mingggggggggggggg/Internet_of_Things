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
            DROP TABLE IF EXISTS performanceTableLatency
            """)
            cur.execute("""
            CREATE TABLE performanceTableLatency (
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
        cur.execute("INSERT INTO performanceTableLatency (datum, timestamp, qos, latency, message) VALUES (?, ?, ?, ?, ?)", (datum, timestamp, qos, latency, message))

