from flask import Blueprint, render_template, request
from flask_login import login_required
from models.log import Log
from .utils import admin_required

logs_bp = Blueprint("logs", __name__, url_prefix="/logs")


@logs_bp.route("/")
@login_required
@admin_required
def index():
    page = request.args.get("page", 1, type=int)
    logs = (
        Log.query
        .order_by(Log.criado_em.desc())
        .paginate(page=page, per_page=60, error_out=False)
    )
    return render_template("logs/index.html", logs=logs)
