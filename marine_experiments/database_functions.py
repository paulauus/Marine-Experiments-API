"""Functions that interact with the database."""

from datetime import datetime
from psycopg2 import connect, extras
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection


def get_db_connection(dbname,
                      password="postgres") -> connection:
    """Returns a DB connection."""

    return connect(dbname=dbname,
                   host="localhost",
                   port=5432,
                   password=password,
                   cursor_factory=RealDictCursor)


def get_subject(conn) -> list[dict]:
    """Returns a list of subjects."""
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

    base_query = """
    SELECT s.subject_id, 
           s.subject_name, 
           sp.species_name, 
           TO_CHAR(s.date_of_birth, 'YYYY-MM-DD') AS date_of_birth
    FROM subject s
    JOIN species sp ON sp.species_id = s.species_id
    ORDER BY s.date_of_birth DESC;
    """
    cursor.execute(base_query)
    rows = cursor.fetchall()

    cursor.close()
    return rows


def get_experiment(conn, type: str = None, score_over: int = None) -> tuple[list[dict], int]:
    """Returns a list of experiments."""
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

    valid_types = {"intelligence", "obedience", "aggression"}

    base_query = """
    SELECT 
        e.experiment_id,
        e.subject_id,
        s.species_name AS species,
        e.experiment_date::TEXT AS experiment_date,
        et.type_name AS experiment_type,
        ROUND((e.score / et.max_score) * 100, 2) || '%' AS score
    FROM 
        experiment e
    JOIN 
        subject sub ON e.subject_id = sub.subject_id
    JOIN 
        species s ON sub.species_id = s.species_id
    JOIN 
        experiment_type et ON e.experiment_type_id = et.experiment_type_id
    """
    conditions = []
    params = []

    # Validate Type
    if type is not None:
        type = str(type).lower()
        if type not in valid_types:
            cursor.close()
            return {"error": "Invalid value for 'type' parameter"}, 400
        conditions.append("LOWER(et.type_name) = %s")
        params.append(type)

    # Validate Score
    if score_over is not None:
        if not isinstance(score_over, int) or score_over < 0 or score_over > 100:
            cursor.close()
            return {"error": "Invalid value for 'score_over' parameter"}, 400
        conditions.append("ROUND((e.score / et.max_score) * 100, 2) > %s")
        params.append(score_over)

    # Add conditions to the query
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    # Add the ORDER BY clause
    base_query += " ORDER BY e.experiment_date DESC;"

    if params:
        cursor.execute(base_query, params)
    else:
        cursor.execute(base_query)
    experiments = cursor.fetchall()

    cursor.close()
    return experiments, 200


def delete_experiment(conn, experiment_id: int):
    """Deletes an experiment with the given ID."""
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

    try:
        # Check if the experiment exists
        check_query = """
        SELECT experiment_id, experiment_date
        FROM experiment
        WHERE experiment_id = %s;
        """
        cursor.execute(check_query, (experiment_id,))
        experiment = cursor.fetchone()

        if not experiment:
            return {"error": f"Unable to locate experiment with ID {experiment_id}."}, 404

        # Delete the experiment
        delete_query = """
        DELETE FROM experiment
        WHERE experiment_id = %s
        RETURNING experiment_id, experiment_date;
        """
        cursor.execute(delete_query, (experiment_id,))
        deleted_experiment = cursor.fetchone()

        if not deleted_experiment:
            return {"error": f"Unable to delete experiment with ID {experiment_id}."}, 500

        # Commit changes to the database
        conn.commit()

        return {
            "experiment_id": deleted_experiment["experiment_id"],
            "experiment_date": deleted_experiment["experiment_date"].strftime('%Y-%m-%d')
        }, 200
    finally:
        cursor.close()


def insert_experiment(conn, subject_id: int, experiment_type: str, score: int, experiment_date: str = None):
    """Inserts a new experiment into the database and returns the inserted data."""
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

    # Validate subject_id
    if not isinstance(subject_id, int) or subject_id <= 0:
        cursor.close()
        return {"error": "Invalid value for 'subject_id' parameter."}, 400

    # Validate experiment_type
    valid_types = {"intelligence", "obedience", "aggression"}
    experiment_type = experiment_type.lower()
    if experiment_type not in valid_types:
        cursor.close()
        return {"error": "Invalid value for 'experiment_type' parameter"}, 400

    # Validate score
    if not isinstance(score, int) or not (0 <= score <= 100):
        cursor.close()
        return {"error": "Invalid value for 'score' parameter"}, 400

    # Set the experiment date
    if experiment_date:
        try:
            experiment_date = datetime.datetime.strptime(
                experiment_date, "%Y-%m-%d").date()
        except ValueError:
            cursor.close()
            return {"error": "Invalid value for 'experiment_date' parameter"}, 400
    else:
        experiment_date = datetime.date.today()

    # Get the experiment_type_id
    cursor.execute("""
        SELECT experiment_type_id FROM experiment_type
        WHERE LOWER(type_name) = %s;
    """, (experiment_type,))
    experiment_type_id = cursor.fetchone()

    if not experiment_type_id:
        cursor.close()
        return {"error": "Invalid 'experiment_type' parameter"}, 400

    experiment_type_id = experiment_type_id["experiment_type_id"]

    # Insert the experiment
    insert_query = """
    INSERT INTO experiment (subject_id, experiment_type_id, experiment_date, score)
    VALUES (%s, %s, %s, %s)
    RETURNING experiment_id, subject_id, experiment_type_id, experiment_date, score;
    """

    cursor.execute(insert_query, (subject_id,
                   experiment_type_id, experiment_date, score))
    new_experiment = cursor.fetchone()

    cursor.close()

    return new_experiment, 201
