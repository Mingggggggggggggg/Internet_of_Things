import sqlite3
import flask
import json
import sys
import os


SQLITE_DB_PATH = "./sensordata.db"

app = flask.Flask(__name__)

def readFromDatabase(con):
    with con:
        cursor = con.cursor()
        cursor.execute("""
        SELECT * FROM dhtreadings
        ORDER BY id DESC LIMIT 20
        """)
        readings = cursor.fetchall()
        print(readings)
        return readings
    return None


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route("/")
def main():
    
    return flask.render_template('main1.html', readings=readings)

if __name__ == "__main__":
    print('DHT22 Sensor - Temperatur und Luftfeuchtigkeit')
    try:
        app.run(host='0.0.0.0', port=8181, debug=False)
    except KeyboardInterrupt:
        pass