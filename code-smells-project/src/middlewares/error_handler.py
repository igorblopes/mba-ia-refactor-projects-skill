"""Tratamento de erros centralizado (AP-15).

Controllers/models apenas lançam AppError/ValidationError; o handler formata a
resposta JSON de forma consistente e loga os 500. Substitui o try/except por rota.
"""
import logging

from flask import jsonify

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Erro de domínio com mensagem pública e status HTTP."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


class ValidationError(AppError):
    def __init__(self, message):
        super().__init__(message, status=400)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def _handle_app_error(error):
        return jsonify({"erro": error.message, "sucesso": False}), error.status

    @app.errorhandler(404)
    def _handle_not_found(error):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def _handle_unexpected(error):
        logger.exception("Erro não tratado: %s", error)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
