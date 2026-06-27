"""Camada HTTP fina: mapeia URL+método -> controller e molda a resposta.

Sem regra de negócio e sem SQL aqui. Preserva URLs, métodos e formatos de
resposta originais (refatoração, não reescrita do contrato).
"""
from flask import Blueprint, jsonify, request

from src.config.settings import settings
from src.controllers import (
    health_controller,
    pedido_controller,
    produto_controller,
    relatorio_controller,
    usuario_controller,
)

bp = Blueprint("api", __name__)


@bp.route("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": settings.VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


# ---------- Produtos ----------
@bp.route("/produtos", methods=["GET"])
def listar_produtos():
    return jsonify({"dados": produto_controller.listar(), "sucesso": True}), 200


@bp.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    resultados = produto_controller.buscar(
        termo=request.args.get("q", ""),
        categoria=request.args.get("categoria"),
        preco_min=request.args.get("preco_min"),
        preco_max=request.args.get("preco_max"),
    )
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


@bp.route("/produtos/<int:produto_id>", methods=["GET"])
def buscar_produto(produto_id):
    return jsonify({"dados": produto_controller.obter(produto_id), "sucesso": True}), 200


@bp.route("/produtos", methods=["POST"])
def criar_produto():
    novo_id = produto_controller.criar(request.get_json(silent=True))
    return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


@bp.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):
    produto_controller.atualizar(produto_id, request.get_json(silent=True))
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


@bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
def deletar_produto(produto_id):
    produto_controller.remover(produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


# ---------- Usuários ----------
@bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    return jsonify({"dados": usuario_controller.listar(), "sucesso": True}), 200


@bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
def buscar_usuario(usuario_id):
    return jsonify({"dados": usuario_controller.obter(usuario_id), "sucesso": True}), 200


@bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    novo_id = usuario_controller.criar(request.get_json(silent=True))
    return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201


@bp.route("/login", methods=["POST"])
def login():
    usuario = usuario_controller.autenticar(request.get_json(silent=True))
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200


# ---------- Pedidos ----------
@bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    resultado = pedido_controller.criar(request.get_json(silent=True))
    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso",
    }), 201


@bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    return jsonify({"dados": pedido_controller.listar_todos(), "sucesso": True}), 200


@bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    return jsonify({
        "dados": pedido_controller.listar_por_usuario(usuario_id),
        "sucesso": True,
    }), 200


@bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    pedido_controller.atualizar_status(pedido_id, request.get_json(silent=True))
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


# ---------- Relatórios & Health ----------
@bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    return jsonify({"dados": relatorio_controller.gerar_relatorio_vendas(), "sucesso": True}), 200


@bp.route("/health", methods=["GET"])
def health_check():
    return jsonify(health_controller.status()), 200
