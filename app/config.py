"""
app/config.py
Configuration settings loaded from environment variables (.env).
Strictly uses crimedb_app for runtime web application operations.
"""
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(basedir, ".env"))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "criminal-dbms-super-secret-key-project-eval")
    
    # Runtime Application Account (Least Privilege)
    DB_USER = os.getenv("DB_APP_USER", "crimedb_app")
    DB_PASSWORD = os.getenv("DB_APP_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_NAME = os.getenv("DB_NAME", "crime_db")
    
    # SQLAlchemy URI using PyMySQL driver
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20
    }
    
    # Chicago Open Data API Settings
    CHICAGO_API_LIMIT = int(os.getenv("CHICAGO_API_LIMIT", 500))
    CHICAGO_API_MAX = int(os.getenv("CHICAGO_API_MAX", 5000))
    CHICAGO_API_URL = "https://data.cityofchicago.org/resource/ijzp-q8t2.json"
