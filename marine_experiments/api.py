"""An API for handling marine experiments."""

from datetime import datetime

from flask import Flask, jsonify, request
from psycopg2 import sql, extras

from database_functions import get_db_connection, get_subject, get_experiment, delete_experiment, insert_experiment


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
    if request.method == "POST":
        data = request.get_json()

        # Extract and validate fields
        subject_id = data.get("subject_id")
        experiment_type = data.get("experiment_type")
        score = data.get("score")
        experiment_date = data.get("experiment_date", None)

        # Specific checks for each required field
        if subject_id is None:
            return jsonify({"error": "Request missing key 'subject_id'."}), 400
        if experiment_type is None:
            return jsonify({"error": "Request missing key 'experiment_type'."}), 400
        if score is None:
            return jsonify({"error": "Request missing key 'score'."}), 400

        # Call the database function
        response, status_code = insert_experiment(
            conn,
            subject_id,
            experiment_type,
            score,
            experiment_date
        )
        conn.commit()
        return jsonify(response), status_code
    
    type = request.args.get('type')
    score_over = request.args.get('score_over')

    try:
        score_over = int(score_over) if score_over is not None else None
    except ValueError:
        return jsonify({"error": "Invalid value for 'score_over' parameter"}), 400

    experiments, status_code = get_experiment(conn, type, score_over)
    return jsonify(experiments), status_code

if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.config["TESTING"] = True

    app.run(port=8000, debug=True)

    conn.close()


@app.route("/experiment/<int:experiment_id>", methods=["DELETE"])
def endpoint_delete_experiment(experiment_id):
    """Deletes an experiment with the given id."""
    response, status_code = delete_experiment(conn, experiment_id)
    return jsonify(response), status_code

