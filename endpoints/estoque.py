from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import db
from models.produto import Produto
from services.logger import snapshot, log_criacao, log_atualizacao, log_exclusao
from .utils import admin_required

estoque_bp = Blueprint("estoque", __name__, url_prefix="/estoque")


@estoque_bp.route("/")
@login_required
def index():
    busca = request.args.get("busca", "")
    tag = request.args.get("tag", "")
    query = Produto.query.filter_by(ativo=True)
    if busca:
        query = query.filter(
            db.or_(
                Produto.nome.ilike(f"%{busca}%"),
                Produto.codigo.ilike(f"%{busca}%"),
                Produto.tag.ilike(f"%{busca}%"),
            )
        )
    if tag:
        query = query.filter(Produto.tag == tag)
    produtos = query.order_by(Produto.nome).all()
    tags = db.session.query(Produto.tag).filter(
        Produto.ativo == True, Produto.tag != None, Produto.tag != ""
    ).distinct().order_by(Produto.tag).all()
    tags = [t[0] for t in tags]
    return render_template("estoque/index.html", produtos=produtos, busca=busca, tag=tag, tags=tags)


@estoque_bp.route("/novo", methods=["GET", "POST"])
@login_required
@admin_required
def novo():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Nome é obrigatório.", "danger")
            return render_template("estoque/form.html", produto=None)

        codigo = request.form.get("codigo", "").strip() or None
        produto = Produto(
            nome=nome,
            descricao=request.form.get("descricao", "").strip(),
            codigo=codigo,
            tag=request.form.get("tag", "").strip() or None,
            preco=float(request.form.get("preco", 0) or 0),
            preco_custo=float(request.form.get("preco_custo", 0) or 0),
            quantidade=int(request.form.get("quantidade", 0) or 0),
            estoque_minimo=int(request.form.get("estoque_minimo", 5) or 5),
        )
        db.session.add(produto)
        try:
            db.session.flush()
            entrada = log_criacao("produto", produto)
            db.session.add(entrada)
            db.session.commit()
            flash("Produto cadastrado com sucesso!", "success")
            return redirect(url_for("estoque.index"))
        except Exception:
            db.session.rollback()
            flash("Código já cadastrado. Use outro código.", "danger")

    return render_template("estoque/form.html", produto=None)


@estoque_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
@admin_required
def editar(id):
    produto = db.get_or_404(Produto, id)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Nome é obrigatório.", "danger")
            return render_template("estoque/form.html", produto=produto)

        antes = snapshot(produto)

        produto.nome = nome
        produto.descricao = request.form.get("descricao", "").strip()
        produto.codigo = request.form.get("codigo", "").strip() or None
        produto.tag = request.form.get("tag", "").strip() or None
        produto.preco = float(request.form.get("preco", 0) or 0)
        produto.preco_custo = float(request.form.get("preco_custo", 0) or 0)
        produto.quantidade = int(request.form.get("quantidade", 0) or 0)
        produto.estoque_minimo = int(request.form.get("estoque_minimo", 5) or 5)

        entrada = log_atualizacao("produto", antes, produto)
        db.session.add(entrada)
        try:
            db.session.commit()
            flash("Produto atualizado com sucesso!", "success")
            return redirect(url_for("estoque.index"))
        except Exception:
            db.session.rollback()
            flash("Erro ao atualizar: código já em uso.", "danger")

    return render_template("estoque/form.html", produto=produto)


@estoque_bp.route("/<int:id>/excluir", methods=["POST"])
@login_required
@admin_required
def excluir(id):
    produto = db.get_or_404(Produto, id)
    entrada = log_exclusao("produto", produto)
    produto.ativo = False
    db.session.add(entrada)
    db.session.commit()
    flash(f'Produto "{produto.nome}" removido.', "success")
    return redirect(url_for("estoque.index"))
