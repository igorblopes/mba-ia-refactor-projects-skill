"""Casos de uso de produto: validação e regras, delegando dados ao model."""
from src.config.constants import (
    CATEGORIAS_VALIDAS,
    CATEGORIA_PADRAO,
    NOME_MAX,
    NOME_MIN,
)
from src.database import get_db
from src.middlewares.error_handler import AppError, ValidationError
from src.models import produto_model


def listar():
    return produto_model.get_all(get_db())


def obter(produto_id):
    produto = produto_model.get_by_id(get_db(), produto_id)
    if not produto:
        raise AppError("Produto não encontrado", 404)
    return produto


def criar(dados):
    campos = _validar(dados)
    db = get_db()
    novo_id = produto_model.create(db, *campos)
    db.commit()
    return novo_id


def atualizar(produto_id, dados):
    db = get_db()
    if not produto_model.get_by_id(db, produto_id):
        raise AppError("Produto não encontrado", 404)
    campos = _validar(dados)
    produto_model.update(db, produto_id, *campos)
    db.commit()


def remover(produto_id):
    db = get_db()
    if not produto_model.get_by_id(db, produto_id):
        raise AppError("Produto não encontrado", 404)
    produto_model.delete(db, produto_id)
    db.commit()


def buscar(termo=None, categoria=None, preco_min=None, preco_max=None):
    db = get_db()
    return produto_model.search(
        db,
        termo or None,
        categoria,
        _to_float(preco_min, "preco_min"),
        _to_float(preco_max, "preco_max"),
    )


def _validar(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    if "nome" not in dados:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in dados:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in dados:
        raise ValidationError("Estoque é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    return nome, descricao, preco, estoque, categoria


def _to_float(valor, campo):
    if valor in (None, ""):
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        raise ValidationError(f"{campo} inválido")
