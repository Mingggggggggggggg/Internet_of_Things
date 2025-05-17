from flask import Flask, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)
db_dir = "performanceTester/results"

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def load_all_data():
    result = []
    for filename in os.listdir(db_dir):
        if filename.endswith(".db"):
            filepath = os.path.join(db_dir, filename)
            con = sqlite3.connect(filepath)
            con.row_factory = dict_factory
            cur = con.cursor()
            try:
                cur.execute("SELECT * FROM performanceTableLatency")
                rows = cur.fetchall()
                for row in rows:
                    row['qos'] = extract_qos_from_filename(filename)
                    result.append(row)
            except Exception as e:
                print(f"Fehler beim Lesen von {filename}: {e}")
            finally:
                con.close()
    return result

def extract_qos_from_filename(filename):
    # z. B. performance0.db → 0
    return int(filename.replace("performance", "").replace(".db", ""))

@app.route("/data")
def get_data():
    return jsonify(load_all_data())

@app.route("/")
def index():
    return render_template("main.html")

def startServer():
    try:
        app.run(host='localhost', port=8181, debug=False)
    except KeyboardInterrupt:
        print("Programm beendet")
