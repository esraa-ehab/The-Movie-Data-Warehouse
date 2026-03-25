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
url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}"

response = requests.get(url)
movies = response.json()["results"]

for movie in movies:
    cur.execute("""
        insert into movies (movie_id, title, release_date, rating, vote_count, language, adult, overview)
        values (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        movie['id'],
        movie['title'],
        movie['release_date'],
        movie['vote_average'],
        movie['vote_count'],
        movie['original_language'],
        movie['adult'],
        movie['overview']
    ))

conn.commit()
cur.close()
conn.close()