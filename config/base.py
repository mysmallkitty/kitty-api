import os

PASSWORD_SALT = os.environ.get("PASSWORD_SALT")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_ACCESS_MINUTES = int(os.environ.get("JWT_EXPIRATION_MINUTES", "60"))
JWT_REFRESH_DAYS = int(os.environ.get("JWT_REFRESH_TOKEN_DAYS", "1"))
JWT_REMEMBER_ME_REFRESH_DAYS = int(os.environ.get("JWT_REMEMBER_ME_REFRESH_DAYS", "30"))
STORAGE_PATH = os.environ.get("STORAGE_PATH", "storage")

# --- ENV CONFIG ---
DEBUG_MODE: bool
HOST: str
PORT: int
DB_URL: str
