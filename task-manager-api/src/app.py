"""Composition root — monta a configuração, o banco, os middlewares e as rotas.

Fino e declarativo: o único lugar que sabe como tudo é conectado.
"""
import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import settings
from src.database import db
from src.middlewares.error_handler import register_error_handlers
from src.views.category_routes import category_bp
from src.views.health_routes import health_bp
from src.views.report_routes import report_bp
from src.views.task_routes import task_bp
from src.views.user_routes import user_bp


def create_app():
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = (
        settings.SQLALCHEMY_TRACK_MODIFICATIONS
    )
    app.config["SECRET_KEY"] = settings.SECRET_KEY

    CORS(app)
    db.init_app(app)

    # Garante que os models estejam registrados antes do create_all.
    from src import models  # noqa: F401

    app.register_blueprint(health_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(report_bp)

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app
