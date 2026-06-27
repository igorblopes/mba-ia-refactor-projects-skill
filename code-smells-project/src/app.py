"""Composition root: carrega config, conecta middlewares, models, controllers e rotas."""
import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import settings
from src.database import close_db, init_db
from src.middlewares.error_handler import register_error_handlers
from src.views.routes import bp


def create_app():
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    CORS(app)
    app.teardown_appcontext(close_db)
    app.register_blueprint(bp)
    register_error_handlers(app)

    init_db(app)
    return app
