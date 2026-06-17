import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

API_KEY: str = os.environ["TMDB_API_KEY"]

POPULARITY_THRESHOLD: float = 0.5
BATCH_SIZE: int = 50
MAX_WORKERS: int = 10


def get_connection() -> psycopg2.extensions.connection:
    dbname = os.environ["DB_NAME"]
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")

    try:
        return psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    except psycopg2.OperationalError as e:
        if host != "localhost":
            try:
                return psycopg2.connect(dbname=dbname, user=user, password=password, host="localhost", port=port)
            except Exception:
                pass
        raise