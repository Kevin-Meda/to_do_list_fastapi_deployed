import os

# Only load .env if not already set (for local dev)
if not os.getenv("DATABASE_URL"):
    from dotenv import load_dotenv
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY_HASHED_PASS = os.getenv("SECRET_KEY_HASHED_PASS")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")