from datetime import datetime
from . import db


class Produto(db.Model):
    __tablename__ = "produtos"
    __table_args__ = (
        db.CheckConstraint("preco >= 0", name="ck_produtos_preco_nao_negativo"),
        db.CheckConstraint(
            "preco_custo >= 0",
            name="ck_produtos_preco_custo_nao_negativo",
        ),
        db.CheckConstraint(
            "quantidade >= 0",
            name="ck_produtos_quantidade_nao_negativa",
        ),
        db.CheckConstraint(
            "estoque_minimo >= 0",
            name="ck_produtos_estoque_minimo_nao_negativo",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    codigo = db.Column(db.String(50), unique=True)
    tag = db.Column(db.String(100))
    preco = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    preco_custo = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    estoque_minimo = db.Column(db.Integer, default=5)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    itens_venda = db.relationship("ItemVenda", backref="produto", lazy=True)
