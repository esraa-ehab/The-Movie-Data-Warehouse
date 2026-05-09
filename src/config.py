import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_connection():
    return psycopg2.connect(
        dbname="MovieVerse_DB",
        user="postgres",
        password="postgres1234",
        host="localhost",
        port="5432"
    )