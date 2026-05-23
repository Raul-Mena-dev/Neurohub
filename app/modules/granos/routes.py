from flask import Blueprint

from app.common.responses import success_response

granos_bp = Blueprint("granos", __name__)


@granos_bp.get("/status")
def status():
    return success_response(data={}, message="Granos module ready")
