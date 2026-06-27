"""Configuração da aplicação — lida do ambiente, sem segredos hardcoded.

Defaults sensatos apenas para desenvolvimento. Em produção, defina as variáveis
de ambiente (SECRET_KEY, FLASK_DEBUG, DB_PATH, PORT, HOST).
"""
import os


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
    VERSION = "1.0.0"


settings = Settings()
