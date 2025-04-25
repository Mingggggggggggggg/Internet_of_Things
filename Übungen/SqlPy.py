import sqlite3


con = sqlite3.connect("dht22.db")

cur = con.cursor()
cur.execute("SELECT SQLITE_VERSION()")


cur.execute("INSERT INTO dhtreadings VALUES(?, ?, ?, ?, ?)", (2, 20, 50, "2025-04-25", "12:55:56"))
con.commit()