import os

DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
DB_URL = os.environ.get("DATABASE_URL", "sqlite://db.sqlite3")
