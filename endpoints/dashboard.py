from flask import Blueprint, render_template
from flask_login import login_required
from models import db
from models.usuario import Usuario
from models.produto import Produto
from models.venda import Venda
from .utils import admin_required
from datetime import date

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
@admin_required
def index():
    hoje = date.today()

    vendas_hoje = Venda.query.filter(
        db.func.date(Venda.criado_em) == hoje
    ).all()

    total_hoje = sum(v.total for v in vendas_hoje)
    total_produtos = Produto.query.filter_by(ativo=True).count()
    produtos_baixo_estoque = Produto.query.filter(
        Produto.quantidade <= Produto.estoque_minimo,
        Produto.ativo == True
    ).all()
    total_usuarios = Usuario.query.filter_by(ativo=True).count()
    ultimas_vendas = Venda.query.order_by(Venda.criado_em.desc()).limit(10).all()

    return render_template(
        "dashboard/index.html",
        total_hoje=total_hoje,
        qtd_vendas_hoje=len(vendas_hoje),
        total_produtos=total_produtos,
        produtos_baixo_estoque=produtos_baixo_estoque,
        total_usuarios=total_usuarios,
        ultimas_vendas=ultimas_vendas,
    )
