from functools import wraps

from flask import current_app, request

from app.common.responses import error_response
from app.modules.caramelo.models import Sucursal


def require_api_key(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        header_name = current_app.config.get("API_KEY_HEADER", "X-API-Key")
        received_api_key = request.headers.get(header_name)

        if not received_api_key:
            return error_response("API key requerida", status_code=401)

        global_api_key = current_app.config.get("API_KEY")
        if global_api_key and received_api_key == global_api_key:
            return view_func(*args, **kwargs)

        sucursal_id = _get_sucursal_id()
        if sucursal_id:
            sucursal = Sucursal.query.filter_by(id=sucursal_id, activa=True).first()
            if sucursal and sucursal.api_key_hash == received_api_key:
                return view_func(*args, **kwargs)

        return error_response("API key invalida", status_code=401)

    return wrapper


def _get_sucursal_id():
    if request.method == "GET":
        return request.args.get("sucursal_id")

    payload = request.get_json(silent=True) or {}
    return payload.get("sucursal_id")
