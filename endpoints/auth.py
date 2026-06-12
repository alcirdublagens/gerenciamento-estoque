from urllib.parse import urlsplit
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.usuario import Usuario
from services.logger import log_acao

auth_bp = Blueprint("auth", __name__)


def _destino_seguro(destino):
    if not destino:
        return None
    parsed = urlsplit(destino)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
        return None
    return destino


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = Usuario.query.filter_by(email=email, ativo=True).first()
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)
            entrada = log_acao("login", email)
            db.session.add(entrada)
            db.session.commit()
            if usuario.deve_trocar_senha:
                return redirect(url_for("auth.alterar_senha"))
            next_page = _destino_seguro(request.args.get("next"))
            return redirect(next_page or url_for("index"))
        flash("Email ou senha incorretos.", "danger")

    return render_template("login.html")


@auth_bp.route("/alterar-senha", methods=["GET", "POST"])
@login_required
def alterar_senha():
    if request.method == "POST":
        senha_atual = request.form.get("senha_atual", "")
        nova_senha = request.form.get("nova_senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        if not current_user.verificar_senha(senha_atual):
            flash("Senha atual incorreta.", "danger")
        elif len(nova_senha) < 12:
            flash("A nova senha deve possuir pelo menos 12 caracteres.", "danger")
        elif nova_senha != confirmar_senha:
            flash("A confirmação da nova senha não confere.", "danger")
        elif nova_senha == senha_atual:
            flash("A nova senha deve ser diferente da senha atual.", "danger")
        else:
            current_user.set_senha(nova_senha)
            current_user.deve_trocar_senha = False
            entrada = log_acao("alterou_senha")
            db.session.add(entrada)
            db.session.commit()
            flash("Senha alterada com sucesso.", "success")
            return redirect(url_for("index"))

    return render_template("alterar_senha.html")


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    saida = log_acao("logout", current_user.email)
    db.session.add(saida)
    db.session.commit()
    logout_user()
    return redirect(url_for("auth.login"))
