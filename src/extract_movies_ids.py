import json
from psycopg2.extras import execute_values
from config import get_connection, POPULARITY_THRESHOLD


def load_movies_to_staging(json_file_path: str) -> None:
    """Bulk-inserts movies from a JSONL file into the staging table."""
    rows = []
    with open(json_file_path, "r") as f:
        for line in f:
            movie = json.loads(line)
            rows.append((movie.get("id"), movie.get("original_title"), movie.get("popularity")))

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                "INSERT INTO raw.staging_movie_ids (tmdb_id, original_title, popularity) VALUES %s",
                rows,
                page_size=1000,
            )
    print(f"Inserted {len(rows)} records.")


def update_status_by_popularity() -> None:
    """Marks rows above the popularity threshold as pending extraction."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE raw.staging_movie_ids SET extraction_status = 'pending' WHERE popularity >= %s",
                (POPULARITY_THRESHOLD,),
            )
    print("Extraction status updated.")


if __name__ == "__main__":
    load_movies_to_staging("src/raw/movie_ids_05_09_2026.json")
    update_status_by_popularity()