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

def get_experiment(conn) -> list[dict]:
    """Returns a list of experiments."""
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
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
    ORDER BY 
        e.experiment_date DESC;
    """
    cursor.execute(base_query)
    experiments = cursor.fetchall()

    cursor.close()
    return experiments
