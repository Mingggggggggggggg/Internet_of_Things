from flask import Flask, jsonify, render_template
import sqlite3
import os
import pMqttHost as mh

app = Flask(__name__)
filepath = f"performanceTester/results/performance{mh.qos}.db"

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

@app.route("/data")
def get_data():
    con = sqlite3.connect(filepath)
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute("SELECT * FROM performanceTableLatency")
    rows = cur.fetchall()
    return jsonify(rows)

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