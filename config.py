import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-mude-em-producao")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _db_url = os.environ.get("DATABASE_URL", "")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url or "sqlite:///estoque.db"

    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
