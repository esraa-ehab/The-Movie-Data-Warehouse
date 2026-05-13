import requests
import psycopg2
from psycopg2.extras import Json, execute_values
import concurrent.futures
import time
from src.config import get_connection, API_KEY

BATCH_SIZE = 50  
MAX_WORKERS = 10 

def fetch_movie_from_api(movie_id):
    """Fetches full movie details and credits from TMDB."""

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        'api_key': API_KEY,
        'append_to_response': 'credits,keywords'
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return movie_id, response.json(), 'completed'
        elif response.status_code == 404:
            return movie_id, None, 'not_found'
        elif response.status_code == 429:
            time.sleep(2)
            return movie_id, None, 'retry'
        
    except Exception as e:
        print(f"Connection error for ID {movie_id}: {e}")
    return movie_id, None, 'failed'

def run_pipeline():
    
    with get_connection() as conn:
        with conn.cursor() as cur:
    
            while True:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT tmdb_id FROM staging.staging_movie_ids 
                        WHERE extraction_status = 'pending' 
                        LIMIT %s
                    """, (BATCH_SIZE,))
                    rows = cur.fetchall()
                    
                if not rows:
                    print("Extraction complete!")
                    break
                    
                ids = [r[0] for r in rows]
                
                results = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    results = list(executor.map(fetch_movie_from_api, ids))
                    
                with conn.cursor() as cur:
                    for m_id, m_json, m_status in results:
                        if m_status == 'completed':
                            cur.execute(
                                "INSERT INTO staging.raw_movies (tmdb_id, movie_data) VALUES (%s, %s) ON CONFLICT (tmdb_id) DO NOTHING",
                                (m_id, Json(m_json))
                            )
                        
                        if m_status == 'retry':
                            m_status = 'Penfing'

                        cur.execute(
                            "UPDATE staging.staging_movie_ids SET extraction_status = %s WHERE tmdb_id = %s",
                            (m_status, m_id)
                        )

                    conn.commit()
                    print(f"Batch processed. Completed {len(ids)} IDs...")

if __name__ == "__main__":
    run_pipeline()