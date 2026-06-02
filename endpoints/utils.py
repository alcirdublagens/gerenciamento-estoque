from functools import wraps
from flask import abort, request
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def log_action(acao, detalhes=""):
    try:
        from models.log import Log
        from models import db
        entry = Log(
            usuario_id=current_user.id,
            acao=acao,
            detalhes=str(detalhes)[:500] if detalhes else "",
            ip=request.remote_addr or "",
        )
        db.session.add(entry)
        db.session.commit()
    except Exception:
        pass
