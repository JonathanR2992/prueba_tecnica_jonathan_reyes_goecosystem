import os
from datetime import timedelta
from urllib.parse import quote_plus

from dotenv import load_dotenv


load_dotenv()


class Config:
    """Configuración principal de la aplicación Flask."""

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "development-flask-secret",
    )

    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "development-jwt-secret",
    )

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "clinica_pacientes")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = quote_plus(
        os.getenv("DB_PASSWORD", "")
    )

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:4200",
    )

    JSON_SORT_KEYS = False