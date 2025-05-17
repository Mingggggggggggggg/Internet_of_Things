import os
import sqlite3
from flask import Flask, jsonify, render_template

app = Flask(__name__)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'performanceTester', 'results')

def load_all_data():
    all_data = []
    for filename in os.listdir(RESULTS_DIR):
        if filename.startswith("performance") and filename.endswith(".db"):
            qos = filename.replace("performance", "").replace(".db", "")
            db_path = os.path.join(RESULTS_DIR, filename)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT datum, qos, latency, messageSize FROM performanceTableLatency")
            rows = cursor.fetchall()
            for row in rows:
                all_data.append({
                    "datum": row["datum"],
                    "qos": row["qos"],
                    "latency": row["latency"],
                    "messageSize": row["messageSize"]
                })
            conn.close()
    return all_data

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/api/latency")
def get_latency():
    data = load_all_data()
    return jsonify(data)

def startServer():
    try:
        app.run(host='localhost', port=8181, debug=False) 
    except KeyboardInterrupt:
        print("Programm beendet")