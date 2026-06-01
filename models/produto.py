from datetime import datetime
from . import db


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    codigo = db.Column(db.String(50), unique=True)
    preco = db.Column(db.Float, nullable=False, default=0.0)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    estoque_minimo = db.Column(db.Integer, default=5)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    itens_venda = db.relationship("ItemVenda", backref="produto", lazy=True)
