import os 
import requests
import psycopg2
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")

conn = psycopg2.connect(
    dbname = "MovieVerse_DB",
    user = "postgres",
    password = "postgres1234",
    host = "localhost",
    port = "5432"
)

cur = conn.cursor()

cur.execute("SELECT movie_id FROM movies;")
movie_ids = [row[0] for row in cur.fetchall()]

for movie_id in movie_ids:
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}"
    credits = requests.get(url).json()
    
IMPORTANT_JOBS = ["Director", "Writer", "Producer"]

for movie_id in movie_ids:
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    credits = requests.get(url).json()

    for member in credits.get('crew', []):
        if member.get('job') not in IMPORTANT_JOBS:
            continue

        cur.execute("""
            INSERT INTO crew (movie_id, name, job, department)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (
            movie_id,
            member.get('name'),
            member.get('job'),
            member.get('department')
        ))

conn.commit()
cur.close()
conn.close()