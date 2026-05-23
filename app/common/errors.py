from werkzeug.exceptions import HTTPException

from app.common.responses import error_response


def register_error_handlers(app):
    @app.errorhandler(400)
    def handle_bad_request(error):
        return error_response("Solicitud invalida", status_code=400)

    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response("Recurso no encontrado", status_code=404)

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        return error_response("Metodo no permitido", status_code=405)

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return error_response(error.description, status_code=error.code)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        if app.config.get("DEBUG"):
            raise error
        return error_response("Error interno del servidor", status_code=500)
