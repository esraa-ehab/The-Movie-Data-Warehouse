import concurrent.futures
import time
from datetime import datetime, timedelta

import requests
from psycopg2.extras import Json

from src.config import get_connection, API_KEY, POPULARITY_THRESHOLD, MAX_WORKERS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tmdb_get(url: str, params: dict, retries: int = 3, backoff: float = 2.0):
    """
    GET wrapper with retry + exponential backoff.
    Handles SSL errors and read timeouts gracefully.
    Returns the Response object or None on permanent failure.
    """
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", backoff * attempt))
                print(f"Rate limited. Waiting {retry_after}s before retry {attempt}/{retries}...")
                time.sleep(retry_after)
                continue
            return resp
        except requests.exceptions.SSLError as e:
            print(f"SSL error on attempt {attempt}/{retries} for {url}: {e}")
        except requests.exceptions.ReadTimeout as e:
            print(f"Read timeout on attempt {attempt}/{retries} for {url}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt}/{retries} for {url}: {e}")

        if attempt < retries:
            time.sleep(backoff * attempt)

    print(f"All {retries} attempts failed for {url}. Skipping.")
    return None


# ---------------------------------------------------------------------------
# Pipeline stages
# ---------------------------------------------------------------------------

def fetch_changed_ids(start_date: str, end_date: str) -> list[int]:
    """
    Collect all changed movie IDs while respecting TMDB limits:
    - Maximum date range per request: 14 days (we use 7-day chunks to be safe)
    - Maximum page number: 500
    """
    all_ids: set[int] = set()
    current_start = datetime.strptime(start_date, "%Y-%m-%d").date()
    final_end = datetime.strptime(end_date, "%Y-%m-%d").date()

    while current_start <= final_end:
        current_end = min(current_start + timedelta(days=6), final_end)
        print(f"Fetching changes: {current_start} -> {current_end}")

        page = 1
        while True:
            resp = _tmdb_get(
                "https://api.themoviedb.org/3/movie/changes",
                params={
                    "api_key": API_KEY,
                    "start_date": current_start.strftime("%Y-%m-%d"),
                    "end_date": current_end.strftime("%Y-%m-%d"),
                    "page": page,
                },
            )

            if resp is None or not resp.ok:
                break

            data = resp.json()
            results = data.get("results", [])
            if not results:
                break

            all_ids.update(movie["id"] for movie in results)

            total_pages = min(data.get("total_pages", 1), 500)
            if page >= total_pages:
                break
            page += 1

        current_start = current_end + timedelta(days=1)

    return list(all_ids)


def sync_staging_metadata(movie_id: int) -> None:
    """
    Lightweight fetch to upsert a movie's title, popularity, and status
    into raw.staging_movie_ids. Each call opens its own DB connection
    so this is safe to run inside a thread pool.
    """
    resp = _tmdb_get(
        f"https://api.themoviedb.org/3/movie/{movie_id}",
        params={"api_key": API_KEY},
    )
    if resp is None or resp.status_code != 200:
        print(f"Skipping movie {movie_id}: could not fetch metadata.")
        return

    data = resp.json()
    title = data.get("original_title")
    pop = data.get("popularity", 0.0)
    status = "pending" if pop >= POPULARITY_THRESHOLD else "skipped"

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO raw.staging_movie_ids
                        (tmdb_id, original_title, popularity, extraction_status, last_updated_at)
                    VALUES
                        (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (tmdb_id) DO UPDATE SET
                        original_title     = EXCLUDED.original_title,
                        popularity         = EXCLUDED.popularity,
                        extraction_status  = CASE
                            WHEN EXCLUDED.popularity >= %s THEN 'pending'
                            ELSE raw.staging_movie_ids.extraction_status
                        END,
                        last_updated_at    = CURRENT_TIMESTAMP
                    """,
                    (movie_id, title, pop, status, POPULARITY_THRESHOLD),
                )
            conn.commit()
    except Exception as e:
        print(f"DB error while syncing movie {movie_id}: {e}")


def deep_extract_and_upsert(movie_id: int) -> None:
    """
    Full fetch (credits + keywords) for a pending movie, written to
    raw.raw_movies. Each call opens its own DB connection.
    """
    resp = _tmdb_get(
        f"https://api.themoviedb.org/3/movie/{movie_id}",
        params={"api_key": API_KEY, "append_to_response": "credits,keywords"},
    )
    if resp is None or resp.status_code != 200:
        print(f"Skipping deep extraction for movie {movie_id}: could not fetch data.")
        return

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO raw.raw_movies (tmdb_id, movie_data, extracted_at)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (tmdb_id) DO UPDATE SET
                        movie_data   = EXCLUDED.movie_data,
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
        print(f"DB error during deep extraction for movie {movie_id}: {e}")


def get_last_run_timestamp() -> str:
    """
    Returns the last successful run timestamp from pipeline_metadata,
    or 24 hours ago as a fallback.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT last_run_timestamp
                FROM raw.pipeline_metadata
                WHERE pipeline_name = 'tmdb_incremental_sync'
                  AND status = 'success'
                ORDER BY last_run_timestamp DESC
                LIMIT 1
                """
            )
            row = cur.fetchone()

    if row:
        return row[0].strftime("%Y-%m-%d")

    fallback = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"No previous successful run found. Defaulting to 24h ago ({fallback}).")
    return fallback


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def run_pipeline() -> None:
    start_date = get_last_run_timestamp()
    end_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Starting incremental sync for {start_date} → {end_date}...")

    # Stage 1: collect changed IDs
    changed_ids = fetch_changed_ids(start_date, end_date)
    print(f"Found {len(changed_ids)} changed IDs. Syncing metadata...")

    # Stage 2: lightweight metadata sync — each thread owns its own connection
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(sync_staging_metadata, changed_ids)

    # Stage 3: deep extraction for popular movies
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT tmdb_id FROM raw.staging_movie_ids WHERE extraction_status = 'pending'"
            )
            pending_ids = [row[0] for row in cur.fetchall()]

    print(f"{len(pending_ids)} movies queued for deep extraction...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(deep_extract_and_upsert, pending_ids)

    print("Pipeline finished successfully.")


if __name__ == "__main__":
    run_pipeline()

    # Record successful run - only reached if run_pipeline() didn't raise
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO raw.pipeline_metadata (pipeline_name, last_run_timestamp, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (pipeline_name) DO UPDATE SET
                    last_run_timestamp = EXCLUDED.last_run_timestamp,
                    status             = EXCLUDED.status
                """,
                ("tmdb_incremental_sync", datetime.now(), "success"),
            )
        conn.commit()