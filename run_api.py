import sys
import pathlib
import os

# Ensure project root is first on sys.path so `api` package imports reliably.
ROOT = pathlib.Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PYTHONPATH", str(ROOT))

import uvicorn
import os

PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "127.0.0.1")

if __name__ == "__main__":
    uvicorn.run("api.main:app", host=HOST, port=PORT, reload=True)
