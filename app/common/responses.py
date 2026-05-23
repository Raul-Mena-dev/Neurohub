from flask import jsonify


def success_response(data=None, message="OK", status_code=200):
    payload = {
        "ok": True,
        "message": message,
        "data": data if data is not None else {},
    }
    return jsonify(payload), status_code


def error_response(message="Error", errors=None, status_code=400):
    payload = {
        "ok": False,
        "message": message,
        "errors": errors if errors is not None else {},
    }
    return jsonify(payload), status_code
