import logging
from datetime import date, timedelta
import click
from flask import Flask, jsonify, redirect, request, url_for
from flask_login import current_user
from flask_wtf.csrf import CSRFError
from config import Config
from models import csrf, db, login_manager, migrate
import models.usuario   # noqa: F401
import models.produto   # noqa: F401
import models.venda     # noqa: F401
import models.cliente   # noqa: F401
import models.log       # noqa: F401

log = logging.getLogger(__name__)


def create_app():
    Config.validate()
    app = Flask(__name__, static_folder="public")
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from endpoints.auth import auth_bp
    from endpoints.dashboard import dashboard_bp
    from endpoints.estoque import estoque_bp
    from endpoints.pdv import pdv_bp
    from endpoints.usuarios import usuarios_bp
    from endpoints.clientes import clientes_bp
    from endpoints.logs import logs_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(estoque_bp)
    app.register_blueprint(pdv_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(logs_bp)

    @app.before_request
    def require_password_change():
        allowed = {"auth.alterar_senha", "auth.logout", "static"}
        if (
            current_user.is_authenticated
            and current_user.deve_trocar_senha
            and request.endpoint not in allowed
        ):
            return redirect(url_for("auth.alterar_senha"))

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        return response

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        if request.is_json:
            return jsonify({"erro": "Sessão expirada. Atualize a página e tente novamente."}), 400
        return error.description, 400

    @app.context_processor
    def inject_notificacoes():
        if current_user.is_authenticated:
            try:
                from models.venda import Venda
                hoje = date.today()
                prazo = hoje + timedelta(days=3)
                count = Venda.query.filter(
                    Venda.status_pagamento == "pendente",
                    Venda.data_vencimento != None,
                    Venda.data_vencimento <= prazo,
                ).count()
                return {"notif_count": count}
            except Exception:
                pass
        return {"notif_count": 0}

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

    @app.cli.command("seed-admin")
    def seed_admin_command():
        created = _seed_admin(app)
        click.echo("Administrador inicial criado." if created else "Administrador já existe.")

    return app


def _seed_admin(app):
    from models.usuario import Usuario
    email = app.config["ADMIN_EMAIL"]
    if Usuario.query.filter_by(email=email).first():
        return False
    senha = app.config["ADMIN_PASSWORD"]
    if len(senha) < 12:
        raise click.ClickException(
            "ADMIN_PASSWORD deve possuir pelo menos 12 caracteres para criar o administrador."
        )
    admin = Usuario(
        nome="Administrador",
        email=email,
        papel="admin",
        deve_trocar_senha=True,
    )
    admin.set_senha(senha)
    db.session.add(admin)
    db.session.commit()
    return True


app = create_app()
