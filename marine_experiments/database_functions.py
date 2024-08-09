"""Functions that interact with the database."""

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
    SELECT s.subject_id, s.subject_name, sp.species_name, s.date_of_birth
    FROM subject s
    JOIN species sp ON sp.species_id = s.species_id;"""
    cursor.execute(base_query)
    rows = cursor.fetchall()

    cursor.close()
    return rows


def get_experiment(conn, type: str = None, score_over: int = None) -> list[dict]:
    """Returns a list of experiments."""
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

    valid_types = {"intelligence", "obedience", "aggression"}

    base_query = """
    SELECT 
        e.experiment_id,
        e.subject_id,
        s.species_name AS species,
        e.experiment_date::TEXT AS experiment_date,
        et.type_name AS experiment_type_name,
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

    # Type
    if type:
        type = type.lower()
        if type not in valid_types:
            cursor.close()
            return {"error": "Invalid value for 'type' parameter"}, 400
        conditions.append("LOWER(et.type_name) = %s")
        params.append(type)

    # Score
    if score_over:
        if not isinstance(score_over, int) or not (0 <= score_over <= 100):
            cursor.close()
            return {"error": "Invalid value for 'score_over' parameter"}, 400
        conditions.append(
            "ROUND((e.score / et.max_score) * 100, 2) > %s")
        params.append(score_over)

    # Add conditions to the query
    if conditions:
        if len(conditions) == 2:
            base_query += " WHERE " + " AND ".join(conditions)
        base_query += " WHERE " + conditions[0]

    # Add the ORDER BY clause
    base_query += " ORDER BY e.experiment_date DESC;"

    if params:
        cursor.execute(base_query, params)
    else:
        cursor.execute(base_query)
    experiments = cursor.fetchall()

    cursor.close()
    return experiments


def delete_experiment():
    ...