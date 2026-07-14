import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

app = FastAPI(
    title="Movie Tracker API",
    description="Backend API for tracking movies and managing user watchlists.",
    version="1.0.0"
)

# Enable CORS so your frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database Connection Pool
try:
    db_pool = SimpleConnectionPool(1, 10, dsn=DATABASE_URL)
except Exception as e:
    print(f"Failed to initialize database pool: {e}")
    db_pool = None

def get_db_connection():
    """Helper to get a connection from the pool."""
    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized.")
    return db_pool.getconn()

def release_db_connection(conn):
    """Helper to release connection back to the pool."""
    if db_pool and conn:
        db_pool.putconn(conn)


# --- Pydantic Schemas for Validation ---

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password_hash: str = Field(..., min_length=6) # In production, use bcrypt on this!

class WatchlistItem(BaseModel):
    user_id: int
    movie_id: int


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Movie Tracker API! Head to /docs for interactive testing."}


### 1. GET /api/movies (Paginated Movies)
@app.get("/api/movies")
def get_movies(
    limit: int = Query(default=20, lte=100, description="Number of records to return"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip")
):
    conn = None
    try:
        conn = get_db_connection()
        # RealDictCursor returns rows as dictionaries instead of tuples
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Query the clean dimension table
            query = """
                SELECT movie_id, title, release_date, genres
                FROM app.dim_movies_clean
                ORDER BY movie_id
                LIMIT %s OFFSET %s;
            """
            cursor.execute(query, (limit, offset))
            movies = cursor.fetchall()
            return {"limit": limit, "offset": offset, "results": movies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            release_db_connection(conn)


### 2. POST /api/users (Create Account)
@app.post("/api/users", status_code=201)
def create_user(user: UserCreate):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Insert the new user and return their generated ID
            query = """
                INSERT INTO app.users (username, email, password_hash, created_at)
                VALUES (%s, %s, %s, NOW())
                RETURNING user_id, username, email;
            """
            cursor.execute(query, (user.username, user.email, user.password_hash))
            new_user = cursor.fetchone()
            conn.commit()
            return {"message": "User created successfully!", "user": new_user}
    except psycopg2.errors.UniqueViolation:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=400, detail="Username or Email already exists.")
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            release_db_connection(conn)


### 3. POST /api/watchlist (Add to Watchlist)
@app.post("/api/watchlist", status_code=201)
def add_to_watchlist(item: WatchlistItem):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Insert item into user watchlist
            query = """
                INSERT INTO app.user_watchlists (user_id, movie_id, added_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (user_id, movie_id) DO NOTHING;
            """
            cursor.execute(query, (item.user_id, item.movie_id))
            conn.commit()
            return {"message": "Movie successfully added to watchlist."}
    except psycopg2.errors.ForeignKeyViolation as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=400, detail="Invalid user_id or movie_id.")
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            release_db_connection(conn)