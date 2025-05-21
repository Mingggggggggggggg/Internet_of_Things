import sqlite3
import csv
import os
from glob import glob

# Konfiguration
RESULTS_DIR = "performanceTester/results"
OUTPUT_DIR = "csv_exports"  

def export_latencies_per_database():
    # Sicherstellen, dass der Output-Ordner existiert
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Alle Datenbankdateien finden
    db_files = glob(os.path.join(RESULTS_DIR, "performance*.db"))
    
    for db_file in db_files:
        try:
            # QoS-Level aus Dateinamen extrahieren
            qos = os.path.basename(db_file).replace("performance", "").replace(".db", "")
            output_csv = os.path.join(OUTPUT_DIR, f"latenzen_qos_{qos}.csv")
            
            # Verbindung zur Datenbank herstellen
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Daten abfragen
            cursor.execute("SELECT * FROM performanceTableLatency")
            
            # CSV-Datei erstellen
            with open(output_csv, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                
                # Header schreiben
                csv_writer.writerow([
                    'ID', 'Datum', 'QoS', 
                    'Latenz (ms)', 'Nachrichtengröße (Bytes)'
                ])
                
                # Daten schreiben
                for row in cursor:
                    csv_writer.writerow(row)
            
            conn.close()
            print(f"Daten aus {os.path.basename(db_file)} exportiert nach: {output_csv}")
            
        except Exception as e:
            print(f"Fehler bei {db_file}: {str(e)}")

if __name__ == "__main__":
    export_latencies_per_database()
    print("Export aller Datenbanken abgeschlossen!")