from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import db
from models.produto import Produto

estoque_bp = Blueprint("estoque", __name__, url_prefix="/estoque")


@estoque_bp.route("/")
@login_required
def index():
    busca = request.args.get("busca", "")
    query = Produto.query.filter_by(ativo=True)
    if busca:
        query = query.filter(Produto.nome.ilike(f"%{busca}%"))
    produtos = query.order_by(Produto.nome).all()
    return render_template("estoque/index.html", produtos=produtos, busca=busca)


@estoque_bp.route("/novo", methods=["GET", "POST"])
@login_required
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
            preco=float(request.form.get("preco", 0) or 0),
            quantidade=int(request.form.get("quantidade", 0) or 0),
            estoque_minimo=int(request.form.get("estoque_minimo", 5) or 5),
        )
        db.session.add(produto)
        try:
            db.session.commit()
            flash("Produto cadastrado com sucesso!", "success")
            return redirect(url_for("estoque.index"))
        except Exception:
            db.session.rollback()
            flash("Código já cadastrado. Use outro código.", "danger")

    return render_template("estoque/form.html", produto=None)


@estoque_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    produto = db.get_or_404(Produto, id)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if not nome:
            flash("Nome é obrigatório.", "danger")
            return render_template("estoque/form.html", produto=produto)

        produto.nome = nome
        produto.descricao = request.form.get("descricao", "").strip()
        produto.codigo = request.form.get("codigo", "").strip() or None
        produto.preco = float(request.form.get("preco", 0) or 0)
        produto.quantidade = int(request.form.get("quantidade", 0) or 0)
        produto.estoque_minimo = int(request.form.get("estoque_minimo", 5) or 5)

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
def excluir(id):
    produto = db.get_or_404(Produto, id)
    produto.ativo = False
    db.session.commit()
    flash(f'Produto "{produto.nome}" removido.', "success")
    return redirect(url_for("estoque.index"))
