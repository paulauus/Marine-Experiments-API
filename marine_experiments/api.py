"""An API for handling marine experiments."""

from datetime import datetime

from flask import Flask, jsonify, request
from psycopg2 import sql, extras

from database_functions import get_db_connection, get_subject, get_experiment


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
def endpoint_get_subject():
    """Returns a list of dictionaries of subjects at /subject."""
    subjects = get_subject(conn)
    return jsonify(subjects), 200


@app.route("/experiment", methods=["GET", "POST"])
def endpoint_experiment():
    """Returns a list of experiments, also enabling POST and DELETE."""
    # Extracting query parameters
    type = request.args.get('type', default=None, type=str)
    score_over = request.args.get('score_over', default=None, type=int)

    # Calling the get_experiment function
    experiments = get_experiment(conn, type, score_over)

    return jsonify(experiments), 200

if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.config["TESTING"] = True

    app.run(port=8000, debug=True)

    conn.close()

@app.route("/experiment/<int:experiment_id>", methods=["DELETE"])
def endpoint_delete_experiment(experiment_id):
    """Deletes an experiment with the given id."""
    
