from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.usuario import Usuario
from services.logger import log_acao

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email, ativo=True).first()
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            entrada = log_acao("login", email)
            db.session.add(entrada)
            db.session.commit()
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        flash("Email ou senha incorretos.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    saida = log_acao("logout", current_user.email)
    db.session.add(saida)
    db.session.commit()
    logout_user()
    return redirect(url_for("auth.login"))
