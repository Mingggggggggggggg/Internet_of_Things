import sqlite3
import os
from datetime import datetime
import csv

filepath = "./dataset.db"
csvPath = "/home/admin/Desktop/Internet_of_Things/hourTracker/Datensatz/Lost Ark Shamewall bereinigt - Tabellenblatt1.csv"



def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d



def readCsv(con, csvPath):
    with open(csvPath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        with con:
            for row in reader:
                try:

                    raw_datum = row["Datum"].strip()
                    datum = datetime.strptime(raw_datum, "%d.%m.%y").date().isoformat()
                        
                    stunden_str = row["Stunden"].replace('"', '').replace(',', '.').strip()
                    stunden = float(stunden_str)
                        
                    insert(con, datum, stunden)

                except Exception as e:
                    print(f" Fehler in Zeile: {row} ; {str(e)}")



def initDB():
    if os.path.exists(filepath):
        os.remove(filepath)

    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory
    
    with con:
        cur = con.cursor()
        cur.execute("""
        CREATE TABLE lostarkshamewall (
            datum DATE PRIMARY KEY,
            stunden NUMERIC,
            relativeStunden NUMERIC
        )
        """)
        tempTable(con)
    return con

def tempTable(con):
    with con:
        cur = con.cursor()
        cur.execute("CREATE TEMP TABLE IF NOT EXISTS _pending (datum DATE, stunden NUMERIC)")
        cur.execute("""
        CREATE TRIGGER IF NOT EXISTS tr_insert_lostarkshamewall
        AFTER INSERT ON _pending
        BEGIN
            DELETE FROM lostarkshamewall WHERE datum = NEW.datum;
            INSERT INTO lostarkshamewall (datum, stunden, relativeStunden)
            VALUES (
                NEW.datum,
                NEW.stunden,
                ROUND(
                    NEW.stunden - COALESCE((
                        SELECT stunden FROM lostarkshamewall
                        WHERE datum < NEW.datum
                        ORDER BY datum DESC LIMIT 1
                    ), 0),1 
                )
            );
        END;
        """)

def insert(con, datum, stunden):
    tempTable(con)  
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO _pending (datum, stunden) VALUES (?, ?)", (datum, stunden))