# Movie Ingestions API + UI

This lightweight FastAPI app serves two endpoints and a small static UI showing movies ingested each day.

Run locally (from project root) after installing dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

If you see "ModuleNotFoundError: No module named 'api'", either run the command from the project root (so Python can import the `api` package), or use one of these alternatives:

```bash
# run with PYTHONPATH set to project root
PYTHONPATH=. uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# or tell uvicorn where the app module lives
uvicorn --app-dir api main:app --reload --host 0.0.0.0 --port 8000
```

Alternatively you can run the included helper which ensures the project root is on `PYTHONPATH`:

```bash
# default port 8000 (avoids Airflow default 8080)
python run_api.py

# or set a custom port (useful if 8000 is taken)
PORT=9000 python run_api.py
```

Open the UI at: http://localhost:8000/

Endpoints:
- `GET /api/ingestions/dates` — returns recent ingestion dates and counts
- `GET /api/ingestions?date=YYYY-MM-DD` — returns movies ingested on that date

The app reads DB connection settings from environment variables (`.env` is supported).
