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

def get_subjects(conn) -> list[dict]:
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
