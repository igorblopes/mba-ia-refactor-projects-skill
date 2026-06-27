"""Tratamento de erros centralizado.

Controllers e models apenas levantam exceções de domínio (`AppError` e
subclasses); este middleware as traduz em respostas JSON consistentes com o
status apropriado. Substitui os `try/except` que devolviam 500 genéricos e os
`except:` pelados espalhados pelas rotas.
"""
import logging

from flask import jsonify

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Erro de domínio com uma mensagem pública e um status HTTP."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


class ValidationError(AppError):
    def __init__(self, message):
        super().__init__(message, 400)


class NotFoundError(AppError):
    def __init__(self, message):
        super().__init__(message, 404)


class ConflictError(AppError):
    def __init__(self, message):
        super().__init__(message, 409)


class UnauthorizedError(AppError):
    def __init__(self, message):
        super().__init__(message, 401)


class ForbiddenError(AppError):
    def __init__(self, message):
        super().__init__(message, 403)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"error": error.message}), error.status

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"error": "Não encontrado"}), 404

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception("Erro não tratado: %s", error)
        return jsonify({"error": "Erro interno"}), 500
