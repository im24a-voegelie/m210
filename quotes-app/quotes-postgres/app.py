import flask
from flask import jsonify, make_response
from flask_cors import CORS
import random
import socket
import os
import psycopg2

app = flask.Flask(__name__)
CORS(app)

def get_db():
    return psycopg2.connect(
        host=os.environ.get("DB_SERVICE_NAME"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD")
    )


def fetch_quotes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, quotation, author FROM quotes")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    h = socket.gethostname()
    return [{"id": r[0], "quotation": r[1], "author": r[2], "hostname": h} for r in rows]

@app.route("/")
def home():
    return make_response("qotd-postgres", 200)

@app.route("/version")
def version():
    return make_response("v1", 200)

@app.route("/quotes")
def getQuotes():
    return jsonify(fetch_quotes())

@app.route("/quotes/random")
def getRandom():
    return jsonify(random.choice(fetch_quotes()))

@app.route("/quotes/<int:id>")
def getById(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, quotation, author FROM quotes WHERE id = %s", (id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"id": r[0], "quotation": r[1], "author": r[2], "hostname": socket.gethostname()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
 # End of recent edits   