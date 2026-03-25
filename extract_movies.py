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

all_movies = []
for page in range(1, 501):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page={page}"
    response = requests.get(url).json()
    if 'results' not in response:
        print(f"Page {page} has no movies, skipping.")
        continue
    all_movies.extend(response['results'])

print(f"Total movies: {len(all_movies)}")

for movie in all_movies:
    release_date = movie.get('release_date')
    if not release_date:  
        release_date = None
    cur.execute("""
        insert into movies (movie_id, title, release_date, rating, vote_count, language, adult, overview)
        values (%s, %s, %s, %s, %s, %s, %s, %s)
        on conflict (movie_id) do nothing
    """, (
        movie['id'],
        movie['title'],
        release_date,
        movie['vote_average'],
        movie['vote_count'],
        movie['original_language'],
        movie['adult'],
        movie['overview']
    ))

conn.commit()
cur.close()
conn.close()