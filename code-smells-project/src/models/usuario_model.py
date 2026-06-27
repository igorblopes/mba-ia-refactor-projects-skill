"""Acesso a dados de usuários. SQL parametrizado; senha sempre hasheada (AP-04)."""
from werkzeug.security import generate_password_hash


def _to_dict(row):
    """Serializa um usuário SEM expor o campo senha (AP-04)."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_all(db):
    rows = db.execute("SELECT * FROM usuarios").fetchall()
    return [_to_dict(row) for row in rows]


def get_by_id(db, usuario_id):
    row = db.execute(
        "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return _to_dict(row) if row else None


def get_by_email(db, email):
    """Linha bruta (inclui hash de senha) — uso interno para autenticação."""
    return db.execute(
        "SELECT * FROM usuarios WHERE email = ?", (email,)
    ).fetchone()


def create(db, nome, email, senha, tipo="cliente"):
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, generate_password_hash(senha), tipo),
    )
    return cursor.lastrowid


def to_public(row):
    """Expõe o serializer público para a camada de autenticação."""
    return _to_dict(row)


def count(db):
    return db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
