import json
from datetime import datetime
from flask import request
from flask_login import current_user
from models.log import Log


_CAMPOS_EXCLUIDOS = frozenset({"senha_hash", "criado_em", "atualizado_em"})


def snapshot(obj) -> dict:
    """Returns a plain-dict copy of a SQLAlchemy model row, safe to pass to log_atualizacao."""
    result = {}
    for col in obj.__table__.columns:
        if col.name in _CAMPOS_EXCLUIDOS:
            continue
        val = getattr(obj, col.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        result[col.name] = val
    return result


def _diff(antes: dict, depois: dict) -> dict:
    """Returns only the fields that changed, each with 'de' (before) and 'para' (after)."""
    campos = set(antes) | set(depois)
    return {
        campo: {"de": antes.get(campo), "para": depois.get(campo)}
        for campo in campos
        if antes.get(campo) != depois.get(campo)
    }


def _novo_log(acao: str, detalhes: dict) -> Log:
    uid = current_user.id if current_user and current_user.is_authenticated else None
    ip = request.remote_addr or ""
    texto = json.dumps(detalhes, ensure_ascii=False, default=str)
    return Log(usuario_id=uid, acao=acao, detalhes=texto[:500], ip=ip)


def log_criacao(entidade: str, obj) -> Log:
    """Returns a Log recording the creation of obj."""
    return _novo_log(f"criou_{entidade}", {"criado": snapshot(obj)})


def log_atualizacao(entidade: str, snapshot_antes: dict, obj_depois) -> Log:
    """Returns a Log recording only the fields that changed between snapshot_antes and obj_depois."""
    alteracoes = _diff(snapshot_antes, snapshot(obj_depois))
    return _novo_log(f"editou_{entidade}", {"alteracoes": alteracoes})


def log_exclusao(entidade: str, obj) -> Log:
    """Returns a Log recording the state of obj at the time of deletion."""
    return _novo_log(f"excluiu_{entidade}", {"excluido": snapshot(obj)})


def log_acao(acao: str, detalhes: str = "") -> Log:
    """Returns a Log for a generic action (login, logout, venda, etc.)."""
    payload = {"info": detalhes} if detalhes else {}
    return _novo_log(acao, payload)
