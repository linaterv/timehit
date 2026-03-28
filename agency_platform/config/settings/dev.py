"""Development settings."""
import os

from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

# --- Database ---
# Use PostgreSQL when DB env vars or DATABASE_URL are set; fall back to SQLite.
_database_url = os.environ.get("DATABASE_URL")

if _database_url:
    # Requires dj-database-url (already in requirements/dev.txt)
    import dj_database_url

    DATABASES = {"default": dj_database_url.parse(_database_url)}
elif os.environ.get("DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "timehit"),
            "USER": os.environ.get("DB_USER", "timehit"),
            "PASSWORD": os.environ.get("DB_PASSWORD", "timehit"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
# else: SQLite from base.py stays as-is
