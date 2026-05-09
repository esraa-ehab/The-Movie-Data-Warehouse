from psycopg2.extras import execute_values
from src.config import get_connection
import json

POPULARITY_THRESHOLD = 0.5


def load_movies_to_staging(json_file_path: str):
    """
    Loads movie data from a JSONL file into PostgreSQL staging table using bulk insert.
    """

    insert_query = """
    INSERT INTO staging.staging_movie_ids (tmdb_id, original_title, popularity)
    VALUES %s
    """

    rows = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            with open(json_file_path, 'r') as f:
                for line in f:
                    movie = json.loads(line)

                    rows.append((
                        movie.get('id'),
                        movie.get('original_title'),
                        movie.get('popularity')
                    ))

            execute_values(cur, insert_query, rows, page_size=1000)

            print(f"Successfully inserted {len(rows)} records.")


def update_status_by_popularity():
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                    UPDATE staging.staging_movie_ids
                    SET extraction_status = 'pending'
                    WHERE popularity >= %s
                """, (POPULARITY_THRESHOLD,))

            print("Status updated successfully.")


if __name__ == '__main__':
    load_movies_to_staging('src/raw/movie_ids_05_09_2026.json')
    update_status_by_popularity()