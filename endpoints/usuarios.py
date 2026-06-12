from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.usuario import Usuario
from services.logger import snapshot, log_criacao, log_atualizacao, log_exclusao
from .utils import admin_required

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.route("/")
@login_required
@admin_required
def index():
    usuarios = Usuario.query.filter_by(ativo=True).order_by(Usuario.nome).all()
    return render_template("usuarios/index.html", usuarios=usuarios)


@usuarios_bp.route("/novo", methods=["GET", "POST"])
@login_required
@admin_required
def novo():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        papel = request.form.get("papel", "vendedor")

        if not all([nome, email, senha]):
            flash("Todos os campos são obrigatórios.", "danger")
            return render_template("usuarios/form.html", usuario=None)

        if len(senha) < 12:
            flash("A senha deve ter no mínimo 12 caracteres.", "danger")
            return render_template("usuarios/form.html", usuario=None)

        if papel not in {"admin", "vendedor"}:
            flash("Perfil de acesso inválido.", "danger")
            return render_template("usuarios/form.html", usuario=None)

        if Usuario.query.filter_by(email=email).first():
            flash("Email já cadastrado.", "danger")
            return render_template("usuarios/form.html", usuario=None)

        usuario = Usuario(
            nome=nome,
            email=email,
            papel=papel,
            deve_trocar_senha=True,
        )
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.flush()
        entrada = log_criacao("usuario", usuario)
        db.session.add(entrada)
        db.session.commit()
        flash("Usuário criado com sucesso!", "success")
        return redirect(url_for("usuarios.index"))

    return render_template("usuarios/form.html", usuario=None)


@usuarios_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar(id):
    usuario = db.get_or_404(Usuario, id)

    if request.method == "POST":
        antes = snapshot(usuario)

        nome = request.form.get("nome", "").strip()
        papel = request.form.get("papel", "vendedor")
        if not nome:
            flash("Nome é obrigatório.", "danger")
            return render_template("usuarios/form.html", usuario=usuario)
        if papel not in {"admin", "vendedor"}:
            flash("Perfil de acesso inválido.", "danger")
            return render_template("usuarios/form.html", usuario=usuario)

        usuario.nome = nome
        usuario.papel = papel
        senha = request.form.get("senha", "")
        if senha:
            if len(senha) < 12:
                flash("A senha deve ter no mínimo 12 caracteres.", "danger")
                return render_template("usuarios/form.html", usuario=usuario)
            usuario.set_senha(senha)
            usuario.deve_trocar_senha = True

        entrada = log_atualizacao("usuario", antes, usuario)
        db.session.add(entrada)
        db.session.commit()
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("usuarios.index"))

    return render_template("usuarios/form.html", usuario=usuario)


@usuarios_bp.route("/<int:id>/excluir", methods=["POST"])
@login_required
@admin_required
def excluir(id):
    usuario = db.get_or_404(Usuario, id)
    if usuario.id == current_user.id:
        flash("Você não pode desativar sua própria conta.", "danger")
        return redirect(url_for("usuarios.index"))
    entrada = log_exclusao("usuario", usuario)
    usuario.ativo = False
    db.session.add(entrada)
    db.session.commit()
    flash(f'Usuário "{usuario.nome}" desativado.', "success")
    return redirect(url_for("usuarios.index"))
