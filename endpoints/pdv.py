from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.produto import Produto
from models.venda import Venda, ItemVenda

pdv_bp = Blueprint("pdv", __name__, url_prefix="/pdv")


@pdv_bp.route("/")
@login_required
def index():
    return render_template("pdv/index.html")


@pdv_bp.route("/produtos")
@login_required
def buscar_produtos():
    termo = request.args.get("q", "").strip()
    query = Produto.query.filter_by(ativo=True).filter(Produto.quantidade > 0)
    if termo:
        query = query.filter(
            db.or_(
                Produto.nome.ilike(f"%{termo}%"),
                Produto.codigo.ilike(f"%{termo}%"),
            )
        )
    produtos = query.order_by(Produto.nome).limit(30).all()
    return jsonify([
        {
            "id": p.id,
            "nome": p.nome,
            "codigo": p.codigo or "",
            "preco": p.preco,
            "quantidade": p.quantidade,
        }
        for p in produtos
    ])


@pdv_bp.route("/venda", methods=["POST"])
@login_required
def registrar_venda():
    data = request.get_json(silent=True) or {}
    itens = data.get("itens", [])

    if not itens:
        return jsonify({"erro": "Carrinho vazio."}), 400

    venda = Venda(vendedor_id=current_user.id, total=0)
    db.session.add(venda)
    db.session.flush()

    total = 0.0
    for item in itens:
        produto = db.session.get(Produto, item.get("produto_id"))
        if not produto or not produto.ativo:
            db.session.rollback()
            return jsonify({"erro": f"Produto inválido."}), 400

        qtd = int(item.get("quantidade", 0))
        if qtd <= 0:
            db.session.rollback()
            return jsonify({"erro": f"Quantidade inválida para {produto.nome}."}), 400

        if produto.quantidade < qtd:
            db.session.rollback()
            return jsonify({"erro": f"Estoque insuficiente para '{produto.nome}'. Disponível: {produto.quantidade}."}), 400

        produto.quantidade -= qtd
        subtotal = produto.preco * qtd
        total += subtotal

        db.session.add(ItemVenda(
            venda_id=venda.id,
            produto_id=produto.id,
            quantidade=qtd,
            preco_unitario=produto.preco,
        ))

    venda.total = total
    db.session.commit()
    return jsonify({"sucesso": True, "venda_id": venda.id, "total": total})
