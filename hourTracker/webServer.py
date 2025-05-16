import DbManager as dm
from flask import Flask, jsonify, render_template


app = Flask(__name__)

@app.route("/")
def main():
    return render_template("main.html")

@app.route("/data/absolute")
def absolute_data():
    return jsonify(dm.getAllData())

@app.route("/data/relative")
def relative_data():
    return jsonify(dm.getRelativeData())

def startServer():
    try:
        app.run(host='localhost', port=8181, debug=False) 
    except KeyboardInterrupt:
        print("Programm beendet")