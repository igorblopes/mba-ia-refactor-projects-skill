"""Instância única do SQLAlchemy, inicializada no composition root (app factory)."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
