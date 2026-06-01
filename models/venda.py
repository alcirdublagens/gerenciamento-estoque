from datetime import datetime
from . import db


class Venda(db.Model):
    __tablename__ = "vendas"

    id = db.Column(db.Integer, primary_key=True)
    vendedor_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    total = db.Column(db.Float, nullable=False, default=0.0)
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
