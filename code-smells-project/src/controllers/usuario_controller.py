"""Casos de uso de usuário: cadastro e autenticação por hash de senha (AP-04)."""
from werkzeug.security import check_password_hash

from src.database import get_db
from src.middlewares.error_handler import AppError, ValidationError
from src.models import usuario_model


def listar():
    return usuario_model.get_all(get_db())


def obter(usuario_id):
    usuario = usuario_model.get_by_id(get_db(), usuario_id)
    if not usuario:
        raise AppError("Usuário não encontrado", 404)
    return usuario


def criar(dados):
    if not dados:
        raise ValidationError("Dados inválidos")

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")

    db = get_db()
    novo_id = usuario_model.create(db, nome, email, senha)
    db.commit()
    return novo_id


def autenticar(dados):
    if not dados:
        raise ValidationError("Email e senha são obrigatórios")

    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")

    row = usuario_model.get_by_email(get_db(), email)
    if row is None or not check_password_hash(row["senha"], senha):
        raise AppError("Email ou senha inválidos", 401)

    return usuario_model.to_public(row)
