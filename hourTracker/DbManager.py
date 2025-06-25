import sqlite3
import os
from datetime import datetime
import csv

filepath = "./dataset.db"
csvPath = "hourTracker/Datensatz/Lost Ark Shamewall - bereinigt - Tabellenblatt1.csv"


# Übernommen aus Laborübung 12
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# Lese und bereinige originalen Datensatz und füge in Datenbank ein
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

# Übernommen aus Laborübung 12 connect:with()   
# Stelle eine Verbindung zur Datenbank her, existiert keine Datenbank, wird diese erstellt und gefüllt               
def initDB(createNew: bool):
    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory

    if createNew or not os.path.exists(filepath):
        if os.path.exists(filepath):
            os.remove(filepath)
    else:
        return con
    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory
    with con:
        cur = con.cursor()
        cur.execute("""
        DROP TABLE IF EXISTS lostarkshamewall
        """)
        cur.execute("""
        CREATE TABLE lostarkshamewall (
            datum DATE PRIMARY KEY,
            stunden NUMERIC,
            relativeStunden NUMERIC
        )
        """)
        con.commit()
        tempTable(con)
        readCsv(con, csvPath)

    return con

# Erstellt eine temporäre Tabelle, damit nur die aktuellsten Stunden pro Tag in der Datenbank sind (Datum ist primary key)
# "Idee" und erstellt von DeepSeek
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

# Methode zum Einfügen von Daten in die Datenbank
def insert(con, datum, stunden):
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO _pending (datum, stunden) VALUES (?, ?)", (datum, stunden))

# Methode zum abrufen der absoluten Stunden für den Webserver
def getAllData():
    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute("SELECT datum, stunden FROM lostarkshamewall ORDER BY datum ASC")
    data = cur.fetchall()
    con.close()
    return data

# Methide zum abrufen der relativen Studnen für den Webserver
def getRelativeData():
    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute("SELECT datum, relativeStunden FROM lostarkshamewall ORDER BY datum ASC")
    data = cur.fetchall()
    con.close()
    return data