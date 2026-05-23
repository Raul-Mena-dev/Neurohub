import os

from dotenv import load_dotenv

load_dotenv()


def _get_database_url(default_url):
    url = os.getenv("DATABASE_URL", default_url)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def _get_cors_origins():
    origins = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000",
    )
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


class BaseConfig:
    SERVICE_NAME = os.getenv("SERVICE_NAME", "neurohub")
    SECRET_KEY = os.getenv("SECRET_KEY", "change_me")
    SQLALCHEMY_DATABASE_URI = _get_database_url(
        "postgresql://postgres:postgres@localhost:5432/neurohub_api"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = _get_cors_origins()
    API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
    API_KEY = os.getenv("API_KEY")
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(config_name=None):
    name = config_name or os.getenv("FLASK_ENV", "development")
    return CONFIGS.get(name, DevelopmentConfig)
