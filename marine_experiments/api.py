"""An API for handling marine experiments."""

from datetime import datetime

from flask import Flask, jsonify, request
from psycopg2 import sql, extras

from database_functions import get_db_connection, get_subjects


app = Flask(__name__)

"""
For testing reasons; please ALWAYS use this connection. 
- Do not make another connection in your code
- Do not close this connection
"""
conn = get_db_connection("marine_experiments")


@app.get("/")
def home():
    """Returns an informational message."""
    return jsonify({
        "designation": "Project Armada",
        "resource": "JSON-based API",
        "status": "Classified"
    })

@app.route("/subject")
def endpoint_get_subjects():
    subjects = get_subjects(conn)
    return jsonify(subjects), 200


if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.config["TESTING"] = True

    app.run(port=8000, debug=True)

    conn.close()
