import concurrent.futures
from datetime import datetime, timedelta

import requests
from psycopg2.extras import Json

from src.config import get_connection, API_KEY, POPULARITY_THRESHOLD, MAX_WORKERS


def fetch_changed_ids(start_date: str, end_date: str) -> list[int]:
    """Paginates through /movie/changes to collect all changed movie IDs."""
    changed_ids = []
    page = 1
    while True:
        response = requests.get(
            "https://api.themoviedb.org/3/movie/changes",
            params={"api_key": API_KEY, "start_date": start_date, "end_date": end_date, "page": page},
        ).json()
        changed_ids.extend(m["id"] for m in response.get("results", []))
        if page >= response.get("total_pages", 1):
            break
        page += 1
    return changed_ids


def sync_staging_metadata(args: tuple) -> None:
    """Lightweight fetch to upsert a movie's metadata into staging."""
    movie_id, conn = args
    try:
        resp = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}", params={"api_key": API_KEY})
        if resp.status_code != 200:
            return
        data = resp.json()
        title = data.get("original_title")
        pop = data.get("popularity", 0.0)
        status = "pending" if pop >= POPULARITY_THRESHOLD else "skipped"

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw.staging_movie_ids (tmdb_id, original_title, popularity, extraction_status, last_updated_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (tmdb_id) DO UPDATE SET
                    original_title = EXCLUDED.original_title,
                    popularity = EXCLUDED.popularity,
                    extraction_status = CASE
                        WHEN EXCLUDED.popularity >= %s THEN 'pending'
                        ELSE raw.staging_movie_ids.extraction_status
                    END,
                    last_updated_at = CURRENT_TIMESTAMP
                """,
                (movie_id, title, pop, status, POPULARITY_THRESHOLD),
            )
            conn.commit()
    except Exception as e:
        print(f"Error syncing staging ID {movie_id}: {e}")


def deep_extract_and_upsert(args: tuple) -> None:
    """Full fetch (credits + keywords) for a pending movie, written to raw_movies."""
    movie_id, conn = args
    try:
        resp = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": API_KEY, "append_to_response": "credits,keywords"},
        )
        if resp.status_code != 200:
            return
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw.raw_movies (tmdb_id, movie_data, extracted_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (tmdb_id) DO UPDATE SET
                    movie_data = EXCLUDED.movie_data,
                    extracted_at = CURRENT_TIMESTAMP
                """,
                (movie_id, Json(resp.json())),
            )
            cur.execute(
                "UPDATE raw.staging_movie_ids SET extraction_status = 'completed' WHERE tmdb_id = %s",
                (movie_id,),
            )
            conn.commit()
    except Exception as e:
        print(f"Deep extraction failed for {movie_id}: {e}")


def get_last_run_timestamp() -> str:
    """Returns the last successful run timestamp from pipeline_metadata, or 24h ago as fallback."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT last_run_timestamp FROM raw.pipeline_metadata
                WHERE pipeline_name = 'tmdb_bulk_insert' AND status = 'success'
                ORDER BY last_run_timestamp DESC
                LIMIT 1
            """)
            row = cur.fetchone()
    if row:
        return row[0].strftime("%Y-%m-%d")
    fallback = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"No previous run found in pipeline_metadata. Defaulting to 24h ago ({fallback}).")
    return fallback


def run_pipeline() -> None:
    start_date = get_last_run_timestamp()
    end_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Starting incremental sync for {start_date} → {end_date}...")

    changed_ids = fetch_changed_ids(start_date, end_date)
    print(f"Found {len(changed_ids)} changed IDs. Syncing metadata...")

    # Reuse a single connection per thread by passing it alongside the ID.
    with get_connection() as conn:
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(sync_staging_metadata, ((mid, conn) for mid in changed_ids))

        with conn.cursor() as cur:
            cur.execute("SELECT tmdb_id FROM raw.staging_movie_ids WHERE extraction_status = 'pending'")
            pending_ids = [row[0] for row in cur.fetchall()]

        print(f"{len(pending_ids)} movies queued for deep extraction...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(deep_extract_and_upsert, ((mid, conn) for mid in pending_ids))

    print("Pipeline finished successfully.")


if __name__ == "__main__":
    run_pipeline()
    with get_connection() as conn:
        with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO raw.pipeline_metadata (
                        pipeline_name,
                        last_run_timestamp,
                        status
                    )
                    VALUES (%s, %s, %s)
                    ON CONFLICT (pipeline_name)
                    DO UPDATE SET
                        last_run_timestamp = EXCLUDED.last_run_timestamp,
                        status = EXCLUDED.status
                    """,
                    ("tmdb_incremental_sync", datetime.now(), "success"),)
        conn.commit()