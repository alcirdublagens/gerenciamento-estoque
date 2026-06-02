import logging
from flask import Flask, redirect, url_for
from flask_login import current_user
from config import Config
from models import db, login_manager
import models.usuario  # noqa: F401
import models.produto  # noqa: F401
import models.venda    # noqa: F401

log = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__, static_folder="public")
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from endpoints.auth import auth_bp
    from endpoints.dashboard import dashboard_bp
    from endpoints.estoque import estoque_bp
    from endpoints.pdv import pdv_bp
    from endpoints.usuarios import usuarios_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(estoque_bp)
    app.register_blueprint(pdv_bp)
    app.register_blueprint(usuarios_bp)

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template("403.html"), 403

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.is_admin:
                return redirect(url_for("dashboard.index"))
            return redirect(url_for("pdv.index"))
        return redirect(url_for("auth.login"))

    with app.app_context():
        try:
            db.create_all()
            _seed_admin()
        except Exception:
            log.exception("Falha ao inicializar banco de dados")

    return app


def _seed_admin():
    from models.usuario import Usuario
    if not Usuario.query.filter_by(email="admin@sistema.com").first():
        admin = Usuario(nome="Administrador", email="admin@sistema.com", papel="admin")
        admin.set_senha("admin123")
        db.session.add(admin)
        db.session.commit()


app = create_app()
