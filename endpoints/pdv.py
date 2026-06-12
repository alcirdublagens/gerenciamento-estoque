from datetime import date as dt_date
from decimal import Decimal
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.produto import Produto
from models.venda import Venda, ItemVenda
from models.cliente import Cliente
from services.logger import log_acao
from .utils import admin_required

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
                Produto.tag.ilike(f"%{termo}%"),
            )
        )
    produtos = query.order_by(Produto.nome).limit(30).all()
    return jsonify([
        {
            "id": p.id,
            "nome": p.nome,
            "codigo": p.codigo or "",
            "tag": p.tag or "",
            "preco": float(p.preco),
            "quantidade": p.quantidade,
        }
        for p in produtos
    ])


@pdv_bp.route("/clientes")
@login_required
def buscar_clientes():
    termo = request.args.get("q", "").strip()
    query = Cliente.query.filter_by(ativo=True)
    if termo:
        query = query.filter(
            db.or_(
                Cliente.nome.ilike(f"%{termo}%"),
                Cliente.identificacao.ilike(f"%{termo}%"),
                Cliente.telefone.ilike(f"%{termo}%"),
            )
        )
    clientes = query.order_by(Cliente.nome).limit(10).all()
    return jsonify([
        {"id": c.id, "nome": c.nome, "identificacao": c.identificacao or ""}
        for c in clientes
    ])


@pdv_bp.route("/venda", methods=["POST"])
@login_required
def registrar_venda():
    data = request.get_json(silent=True) or {}
    itens = data.get("itens", [])

    if not itens:
        return jsonify({"erro": "Carrinho vazio."}), 400

    tipo_pagamento = data.get("tipo_pagamento", "avista")
    cliente_id = data.get("cliente_id") or None
    num_parcelas = data.get("num_parcelas")
    data_vencimento_str = data.get("data_vencimento")
    observacao = data.get("observacao", "")

    if tipo_pagamento not in {"avista", "aprazo", "parcelado"}:
        return jsonify({"erro": "Tipo de pagamento inválido."}), 400

    venc = None
    if data_vencimento_str:
        try:
            venc = dt_date.fromisoformat(data_vencimento_str)
        except ValueError:
            return jsonify({"erro": "Data de vencimento inválida."}), 400

    if tipo_pagamento in ("aprazo", "parcelado") and not venc:
        return jsonify({"erro": "Informe a data de vencimento para este tipo de pagamento."}), 400

    status_pagamento = "pago" if tipo_pagamento == "avista" else "pendente"

    try:
        cliente_id = int(cliente_id) if cliente_id else None
        num_parcelas = int(num_parcelas) if num_parcelas else None
    except (TypeError, ValueError):
        return jsonify({"erro": "Dados da venda inválidos."}), 400

    if cliente_id and not db.session.get(Cliente, cliente_id):
        return jsonify({"erro": "Cliente inválido."}), 400
    if tipo_pagamento == "parcelado" and (not num_parcelas or num_parcelas < 2):
        return jsonify({"erro": "Informe ao menos duas parcelas."}), 400

    venda = Venda(
        vendedor_id=current_user.id,
        cliente_id=cliente_id,
        total=0,
        tipo_pagamento=tipo_pagamento,
        num_parcelas=num_parcelas,
        data_vencimento=venc,
        status_pagamento=status_pagamento,
        observacao=observacao,
    )
    db.session.add(venda)
    db.session.flush()

    total = Decimal("0.00")
    produtos_processados = set()
    for item in itens:
        try:
            produto_id = int(item.get("produto_id"))
            qtd = int(item.get("quantidade", 0))
        except (TypeError, ValueError):
            db.session.rollback()
            return jsonify({"erro": "Item da venda inválido."}), 400

        if produto_id in produtos_processados:
            db.session.rollback()
            return jsonify({"erro": "Produto duplicado no carrinho."}), 400
        produtos_processados.add(produto_id)

        produto = db.session.execute(
            db.select(Produto)
            .where(Produto.id == produto_id)
            .with_for_update()
        ).scalar_one_or_none()
        if not produto or not produto.ativo:
            db.session.rollback()
            return jsonify({"erro": "Produto inválido."}), 400

        if qtd <= 0:
            db.session.rollback()
            return jsonify({"erro": f"Quantidade inválida para {produto.nome}."}), 400

        if produto.quantidade < qtd:
            db.session.rollback()
            return jsonify({"erro": f"Estoque insuficiente para '{produto.nome}'. Disponível: {produto.quantidade}."}), 400

        produto.quantidade -= qtd
        total += produto.preco * qtd

        db.session.add(ItemVenda(
            venda_id=venda.id,
            produto_id=produto.id,
            quantidade=qtd,
            preco_unitario=produto.preco,
            preco_custo_unitario=produto.preco_custo or Decimal("0.00"),
        ))

    venda.total = total
    entrada = log_acao("registrou_venda", f"#{venda.id} — R$ {total:.2f} — {tipo_pagamento}")
    db.session.add(entrada)
    db.session.commit()
    return jsonify({"sucesso": True, "venda_id": venda.id, "total": float(total)})


@pdv_bp.route("/venda/<int:id>/pagar", methods=["POST"])
@login_required
@admin_required
def marcar_pago(id):
    venda = db.get_or_404(Venda, id)
    venda.status_pagamento = "pago"
    entrada = log_acao("marcou_venda_paga", f"#{id}")
    db.session.add(entrada)
    db.session.commit()
    flash(f"Venda #{id} marcada como paga.", "success")
    return redirect(url_for("dashboard.index"))
