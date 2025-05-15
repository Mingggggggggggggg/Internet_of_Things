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
                cursor = con.cursor()
                for row in reader:
                    try:
                                            # 1. Datum von "01.01.24" zu "01.01.2024" konvertieren
                        raw_datum = row["Datum"].strip()
                        dt = datetime.strptime(raw_datum, "%d.%m.%y")  # %y = kurzes Jahr (00-99)
                        datum_deutsch = dt.strftime("%d.%m.%Y")  # %Y = langes Jahr
                        
                        # 2. Für die DB trotzdem ISO-Format (YYYY-MM-DD) verwenden
                        datum_iso = dt.date().isoformat()
                        
                        # Stunden umwandeln ("2003,5" → 2003.5)
                        stunden = float(row["Stunden"].replace(',', '.').strip())
                        
                        # In temporäre Tabelle einfügen
                        cursor.execute(
                            "INSERT INTO _pending (datum, stunden) VALUES (?, ?)",
                            (datum_iso, stunden)
                        )
                        
                        print(f"Importiert: {datum_deutsch} = {stunden} Stunden")  # Debug
                    except Exception as e:
                        print(f"⚠️ Fehler in Zeile: {row} → {str(e)}")



def initDB():
    if os.path.exists(filepath):
        os.remove(filepath)

    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory

    with con:
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
        cur.execute("CREATE TEMP TABLE _pending (datum DATE, stunden NUMERIC)")

        cur.execute("""
        CREATE TRIGGER tr_insert_lostarkshamewall
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
    return con

def insert(con, datum, stunden):
    with con:
        cur = con.cursor()
        cur.execute("INSERT INTO _pending (datum, stunden) VALUES (?, ?)", (datum, stunden))


def insertData(con):
    test_data = [
        ("01.05.2024", 120),
        ("01.05.2024", 130),
        ("01.05.2024", 140),
        ("01.05.2024", 140),
        ("01.05.2024", 145),
        ("01.05.2024", 146),
        ("01.05.2024", 147),
        ("02.05.2024", 148)
    ]
    with con:
        cursor = con.cursor()
        for datum, stunden in test_data:
            cursor.execute("INSERT INTO _pending (datum, stunden) VALUES (?, ?)", (datum, stunden))
        con.commit()

def print_all(con):
    with con:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM lostarkshamewall ORDER BY datum")
        for row in cursor.fetchall():
            print(row)

if __name__ == "__main__":
    con = initDB()
    readCsv(con, csvPath)
