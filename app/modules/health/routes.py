from flask import Blueprint, current_app

from app.common.responses import success_response

health_bp = Blueprint("health", __name__)


@health_bp.get("")
def health_check():
    return success_response(
        data={"service": current_app.config["SERVICE_NAME"]},
        message="API running",
    )
