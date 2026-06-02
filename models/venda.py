from datetime import datetime
from . import db


class Venda(db.Model):
    __tablename__ = "vendas"

    id = db.Column(db.Integer, primary_key=True)
    vendedor_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=True)
    total = db.Column(db.Float, nullable=False, default=0.0)
    tipo_pagamento = db.Column(db.String(20), nullable=False, default="avista")
    num_parcelas = db.Column(db.Integer)
    data_vencimento = db.Column(db.Date)
    status_pagamento = db.Column(db.String(20), nullable=False, default="pago")
    observacao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    itens = db.relationship("ItemVenda", backref="venda", lazy=True)


class ItemVenda(db.Model):
    __tablename__ = "itens_venda"

    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey("vendas.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    preco_custo_unitario = db.Column(db.Float, nullable=False, default=0.0)
