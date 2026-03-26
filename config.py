from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
DATABASE = os.getenv("DATABASE", "vegmart.db")
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB limit
PERMANENT_SESSION_LIFETIME = timedelta(days=30)
