import os

import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from psycopg2.extras import RealDictCursor

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def get_db_connection():
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_port = os.getenv("DB_PORT", "5432")
    requested_host = os.getenv("DB_HOST")
    candidate_hosts = [host for host in [requested_host, "localhost", "127.0.0.1"] if host]

    last_error = None
    for host in candidate_hosts:
        try:
            return psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=host,
                port=db_port,
            )
        except Exception as exc:
            last_error = exc

    raise HTTPException(
        status_code=500,
        detail=f"Unable to connect to Postgres using hosts {candidate_hosts}: {last_error}",
    )


@app.get("/")
def index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail=f"Missing UI file: {index_path}")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/ingestions/dates")
def ingested_dates(limit: int = Query(30, ge=1, le=365)):
    query = """
        SELECT DATE(extracted_at) AS date, COUNT(*) AS count
        FROM raw.raw_movies
        GROUP BY DATE(extracted_at)
        ORDER BY date DESC
        LIMIT %s
    """
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/ingestions")
def ingested_movies(date: str = Query(..., description="YYYY-MM-DD"), limit: int = Query(100, ge=1, le=100)):
    query = """
        SELECT tmdb_id, movie_data, extracted_at
        FROM raw.raw_movies
        WHERE DATE(extracted_at) = %s
        ORDER BY COALESCE((movie_data->>'popularity')::numeric, 0) DESC, extracted_at DESC
        LIMIT %s
    """
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (date, limit))
            rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")), reload=True)
