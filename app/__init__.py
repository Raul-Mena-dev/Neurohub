from flask import Flask

from app.common.errors import register_error_handlers
from app.config import get_config
from app.extensions import cors, db, migrate
from app.modules.caramelo.routes import caramelo_bp
from app.modules.granos.routes import granos_bp
from app.modules.health.routes import health_bp


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
    )

    app.register_blueprint(health_bp, url_prefix="/api/health")
    app.register_blueprint(caramelo_bp, url_prefix="/api/caramelo")
    app.register_blueprint(granos_bp, url_prefix="/api/granos")

    register_error_handlers(app)

    return app
