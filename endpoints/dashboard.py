from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from models import db
from models.usuario import Usuario
from models.produto import Produto
from models.venda import Venda, ItemVenda
from models.cliente import Cliente
from .utils import admin_required
from datetime import date, timedelta

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
@admin_required
def index():
    hoje = date.today()
    trinta_dias = hoje - timedelta(days=30)

    vendas_hoje = Venda.query.filter(func.date(Venda.criado_em) == hoje).all()
    total_hoje = sum(v.total for v in vendas_hoje)

    custo_hoje = db.session.query(
        func.coalesce(func.sum(ItemVenda.preco_custo_unitario * ItemVenda.quantidade), 0.0)
    ).join(Venda).filter(func.date(Venda.criado_em) == hoje).scalar() or 0.0

    lucro_hoje = total_hoje - custo_hoje

    total_produtos = Produto.query.filter_by(ativo=True).count()
    total_clientes = Cliente.query.filter_by(ativo=True).count()

    vendedores_hoje = db.session.query(func.count(func.distinct(Venda.vendedor_id))).filter(
        func.date(Venda.criado_em) == hoje
    ).scalar() or 0

    produtos_baixo_estoque = Produto.query.filter(
        Produto.quantidade <= Produto.estoque_minimo,
        Produto.ativo == True
    ).all()

    ultimas_vendas = Venda.query.order_by(Venda.criado_em.desc()).limit(10).all()

    desempenho = db.session.query(
        Usuario,
        func.count(Venda.id).label("qtd"),
        func.coalesce(func.sum(Venda.total), 0.0).label("total"),
    ).join(Venda, Venda.vendedor_id == Usuario.id).filter(
        Venda.criado_em >= trinta_dias
    ).group_by(Usuario.id).order_by(func.sum(Venda.total).desc()).all()

    prazo = hoje + timedelta(days=3)
    vencendo = Venda.query.filter(
        Venda.status_pagamento == "pendente",
        Venda.data_vencimento != None,
        Venda.data_vencimento >= hoje,
        Venda.data_vencimento <= prazo,
    ).order_by(Venda.data_vencimento).all()

    vencidas = Venda.query.filter(
        Venda.status_pagamento == "pendente",
        Venda.data_vencimento != None,
        Venda.data_vencimento < hoje,
    ).order_by(Venda.data_vencimento).all()

    return render_template(
        "dashboard/index.html",
        total_hoje=total_hoje,
        custo_hoje=custo_hoje,
        lucro_hoje=lucro_hoje,
        qtd_vendas_hoje=len(vendas_hoje),
        total_produtos=total_produtos,
        total_clientes=total_clientes,
        vendedores_hoje=vendedores_hoje,
        produtos_baixo_estoque=produtos_baixo_estoque,
        ultimas_vendas=ultimas_vendas,
        desempenho=desempenho,
        vencendo=vencendo,
        vencidas=vencidas,
    )
