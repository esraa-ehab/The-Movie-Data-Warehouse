import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

API_KEY: str = os.environ["TMDB_API_KEY"]

POPULARITY_THRESHOLD: float = 0.5
BATCH_SIZE: int = 50
MAX_WORKERS: int = 10


def get_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
    )