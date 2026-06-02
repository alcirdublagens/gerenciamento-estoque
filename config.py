import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "chave-secreta-dev-trocar-em-producao")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _db_url = os.environ.get("DATABASE_URL", "")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url or "sqlite:///estoque.db"

    # Em produção (PostgreSQL/Vercel), usa NullPool — cada invocação serverless
    # abre e fecha sua própria conexão sem tentar reutilizá-la entre requests.
    if _db_url:
        from sqlalchemy.pool import NullPool
        SQLALCHEMY_ENGINE_OPTIONS = {
            "poolclass": NullPool,
            "pool_pre_ping": True,
            "connect_args": {"sslmode": "require"},
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
