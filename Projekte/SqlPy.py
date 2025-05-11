import sqlite3


con = sqlite3.connect("dht22.db")

cur = con.cursor()
cur.execute("SELECT SQLITE_VERSION()")


cur.execute("INSERT INTO dhtreadings VALUES(?, ?, ?, ?)", (1, 20, 50, "25.01.2010", "13:23"))
con.commit()