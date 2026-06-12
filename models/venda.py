from datetime import datetime
from . import db


class Venda(db.Model):
    __tablename__ = "vendas"
    __table_args__ = (
        db.CheckConstraint("total >= 0", name="ck_vendas_total_nao_negativo"),
    )

    id = db.Column(db.Integer, primary_key=True)
    vendedor_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=True)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    tipo_pagamento = db.Column(db.String(20), nullable=False, default="avista")
    num_parcelas = db.Column(db.Integer)
    data_vencimento = db.Column(db.Date)
    status_pagamento = db.Column(db.String(20), nullable=False, default="pago")
    observacao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    itens = db.relationship("ItemVenda", backref="venda", lazy=True)


class ItemVenda(db.Model):
    __tablename__ = "itens_venda"
    __table_args__ = (
        db.CheckConstraint(
            "quantidade > 0",
            name="ck_itens_venda_quantidade_positiva",
        ),
        db.CheckConstraint(
            "preco_unitario >= 0",
            name="ck_itens_venda_preco_nao_negativo",
        ),
        db.CheckConstraint(
            "preco_custo_unitario >= 0",
            name="ck_itens_venda_custo_nao_negativo",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey("vendas.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    preco_custo_unitario = db.Column(db.Numeric(12, 2), nullable=False, default=0)
