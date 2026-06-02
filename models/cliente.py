from datetime import datetime
from . import db


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    identificacao = db.Column(db.String(50))
    telefone = db.Column(db.String(30))
    endereco = db.Column(db.String(300))
    email = db.Column(db.String(150))
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    vendas = db.relationship("Venda", backref="cliente", lazy=True)
