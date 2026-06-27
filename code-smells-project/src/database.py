"""Camada de conexão com o banco — conexão por requisição via flask.g.

Substitui o singleton global mutável compartilhado entre threads (AP-09).
Cada requisição obtém sua própria conexão, fechada no teardown.
"""
import sqlite3

from flask import g

from src.config.settings import settings
from src.models import produto_model, usuario_model


def get_db():
    """Conexão SQLite vinculada ao contexto da requisição atual."""
    if "db" not in g:
        g.db = sqlite3.connect(settings.DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    """Fecha a conexão da requisição (registrado como teardown)."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Cria o schema e popula dados de exemplo no primeiro boot."""
    with app.app_context():
        db = get_db()
        _create_schema(db)
        _seed(db)
        db.commit()
        close_db()


def _create_schema(db):
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT,
            preco REAL,
            estoque INTEGER,
            categoria TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            senha TEXT,
            tipo TEXT DEFAULT 'cliente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            status TEXT DEFAULT 'pendente',
            total REAL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            preco_unitario REAL
        )
        """
    )


def _seed(db):
    if db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
        produtos = [
            ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
            ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
            ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
            ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
            ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
            ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
            ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
            ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
            ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
            ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
        ]
        for p in produtos:
            produto_model.create(db, *p)

    if db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        # Senhas hasheadas no seed para que o login continue funcionando (AP-04).
        usuarios = [
            ("Admin", "admin@loja.com", "admin123", "admin"),
            ("João Silva", "joao@email.com", "123456", "cliente"),
            ("Maria Santos", "maria@email.com", "senha123", "cliente"),
        ]
        for nome, email, senha, tipo in usuarios:
            usuario_model.create(db, nome, email, senha, tipo)
