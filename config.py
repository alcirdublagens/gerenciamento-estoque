import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-mude-em-producao")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _db_url = os.environ.get("DATABASE_URL", "")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    if _db_url:
        SQLALCHEMY_DATABASE_URI = _db_url
    elif os.environ.get("DB_HOST"):
        SQLALCHEMY_DATABASE_URI = URL.create(
            drivername="postgresql+psycopg2",
            username=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            host=os.environ["DB_HOST"],
            port=int(os.environ.get("DB_PORT", "5432")),
            database=os.environ.get("DB_NAME"),
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///estoque.db"

    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
