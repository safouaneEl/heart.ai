import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "heart_ai")

# Flask secret key
FLASK_SECRET = os.getenv("FLASK_SECRET", os.urandom(24))
