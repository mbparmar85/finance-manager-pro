import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

@dataclass
class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'finance.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    JSON_SORT_KEYS = False

config = Config()
