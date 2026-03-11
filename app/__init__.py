from flask import Flask

from .config import Config
from .extensions import cache, db
from .routes import dashboard_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    db.init_app(app)
    cache.init_app(app, config={"CACHE_TYPE": "RedisCache", "CACHE_REDIS_URL": app.config["CACHE_REDIS_URL"]})
    app.register_blueprint(dashboard_bp)
    return app
