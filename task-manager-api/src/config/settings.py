"""Configuração da aplicação lida do ambiente — sem segredos hardcoded.

Todos os valores sensíveis (SECRET_KEY, credenciais de e-mail) e parâmetros de
runtime (DEBUG, HOST, PORT, caminho do banco) vêm de variáveis de ambiente, com
defaults seguros apenas para desenvolvimento. Veja `.env.example`.
"""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Núcleo Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    # Banco de dados
    DB_PATH = os.environ.get("DB_PATH", "tasks.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{DB_PATH}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Serviço de notificação por e-mail (SMTP)
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")


settings = Settings()
