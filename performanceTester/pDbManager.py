import sqlite3
import os
import pMqttHost as mh
filepath = f"performanceTester/results/performance{mh.qos}.db"


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d



       
def initDB():
    if os.path.exists(filepath):
        os.remove(filepath)

    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS performanceTableLatency")
        cur.execute("""
        CREATE TABLE performanceTableLatency (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum DATE,
            qos INTEGER,
            latency INTEGER,
            messageSize INTEGER
        )
        """)
        con.commit()
    return con




def insert(con, datum, qos, latency, messageSize):
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO performanceTableLatency (datum,  qos, latency, messageSize) VALUES (?, ?, ?, ?)", (datum, qos, latency, messageSize))

