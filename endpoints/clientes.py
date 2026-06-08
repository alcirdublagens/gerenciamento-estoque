from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from models import db
from models.cliente import Cliente
from services.logger import snapshot, log_criacao, log_atualizacao, log_exclusao

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")


@clientes_bp.route("/")
@login_required
def index():
    busca = request.args.get("busca", "")
    query = Cliente.query.filter_by(ativo=True)
    if busca:
        query = query.filter(
            db.or_(
                Cliente.nome.ilike(f"%{busca}%"),
                Cliente.email.ilike(f"%{busca}%"),
                Cliente.identificacao.ilike(f"%{busca}%"),
                Cliente.telefone.ilike(f"%{busca}%"),
            )
        )
    clientes = query.order_by(Cliente.nome).all()
    return render_template("clientes/index.html", clientes=clientes, busca=busca)


@clientes_bp.route("/buscar")
@login_required
def buscar():
    termo = request.args.get("q", "").strip()
    query = Cliente.query.filter_by(ativo=True)
    if termo:
        query = query.filter(
            db.or_(
                Cliente.nome.ilike(f"%{termo}%"),
                Cliente.identificacao.ilike(f"%{termo}%"),
            )
        )
    clientes = query.order_by(Cliente.nome).limit(10).all()
    return jsonify([
        {"id": c.id, "nome": c.nome, "identificacao": c.identificacao or ""}
        for c in clientes
    ])


@clientes_bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Nome é obrigatório.", "danger")
            return render_template("clientes/form.html", cliente=None)

        cliente = Cliente(
            nome=nome,
            identificacao=request.form.get("identificacao", "").strip(),
            telefone=request.form.get("telefone", "").strip(),
            endereco=request.form.get("endereco", "").strip(),
            email=request.form.get("email", "").strip(),
        )
        db.session.add(cliente)
        db.session.flush()
        entrada = log_criacao("cliente", cliente)
        db.session.add(entrada)
        db.session.commit()
        flash("Cliente cadastrado com sucesso!", "success")
        return redirect(url_for("clientes.index"))

    return render_template("clientes/form.html", cliente=None)


@clientes_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    cliente = db.get_or_404(Cliente, id)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Nome é obrigatório.", "danger")
            return render_template("clientes/form.html", cliente=cliente)

        antes = snapshot(cliente)

        cliente.nome = nome
        cliente.identificacao = request.form.get("identificacao", "").strip()
        cliente.telefone = request.form.get("telefone", "").strip()
        cliente.endereco = request.form.get("endereco", "").strip()
        cliente.email = request.form.get("email", "").strip()

        entrada = log_atualizacao("cliente", antes, cliente)
        db.session.add(entrada)
        db.session.commit()
        flash("Cliente atualizado!", "success")
        return redirect(url_for("clientes.index"))

    return render_template("clientes/form.html", cliente=cliente)


@clientes_bp.route("/<int:id>/excluir", methods=["POST"])
@login_required
def excluir(id):
    cliente = db.get_or_404(Cliente, id)
    entrada = log_exclusao("cliente", cliente)
    cliente.ativo = False
    db.session.add(entrada)
    db.session.commit()
    flash(f'Cliente "{cliente.nome}" removido.', "success")
    return redirect(url_for("clientes.index"))
