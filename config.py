import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "chave-secreta-dev-trocar-em-producao")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Produção (Vercel): defina DATABASE_URL com uma URL PostgreSQL (ex: Neon, Supabase)
    # Desenvolvimento local: usa SQLite automaticamente
    _db_url = os.environ.get("DATABASE_URL", "")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url or "sqlite:///estoque.db"
