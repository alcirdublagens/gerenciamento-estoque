from datetime import datetime
from . import db


class Log(db.Model):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    acao = db.Column(db.String(100), nullable=False)
    detalhes = db.Column(db.Text)
    ip = db.Column(db.String(45))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario", backref=db.backref("logs", lazy=True))
