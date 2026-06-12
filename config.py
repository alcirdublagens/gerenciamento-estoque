import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-mude-em-producao")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    WTF_CSRF_TIME_LIMIT = 12 * 60 * 60

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@sistema.com").strip().lower()
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
    DB_HOST = os.environ.get("DB_HOST", "")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    ENFORCE_SECURE_CONFIG = os.environ.get(
        "ENFORCE_SECURE_CONFIG", ""
    ).lower() in {"1", "true", "yes"}

    _db_url = os.environ.get("DATABASE_URL", "")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    if _db_url:
        SQLALCHEMY_DATABASE_URI = _db_url
    elif DB_HOST:
        SQLALCHEMY_DATABASE_URI = URL.create(
            drivername="postgresql+psycopg2",
            username=os.environ.get("DB_USER"),
            password=DB_PASSWORD,
            host=DB_HOST,
            port=int(os.environ.get("DB_PORT", "5432")),
            database=os.environ.get("DB_NAME"),
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///estoque.db"

    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    @classmethod
    def validate(cls):
        if not cls.ENFORCE_SECURE_CONFIG:
            return
        if len(cls.SECRET_KEY) < 32 or cls.SECRET_KEY.startswith("troque-"):
            raise RuntimeError("SECRET_KEY deve possuir pelo menos 32 caracteres.")
        if len(cls.ADMIN_PASSWORD) < 12 or cls.ADMIN_PASSWORD.startswith("troque-"):
            raise RuntimeError("ADMIN_PASSWORD deve possuir pelo menos 12 caracteres.")
        if cls.DB_HOST and (
            len(cls.DB_PASSWORD) < 12 or cls.DB_PASSWORD.startswith("troque-")
        ):
            raise RuntimeError("POSTGRES_PASSWORD deve possuir pelo menos 12 caracteres.")
        if "@" not in cls.ADMIN_EMAIL:
            raise RuntimeError("ADMIN_EMAIL deve ser um endereço de email válido.")
