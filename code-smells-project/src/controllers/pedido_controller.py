"""Casos de uso de pedido: regras de estoque/total, transação e notificações."""
from src.config.constants import STATUS_PEDIDO_INICIAL, STATUS_PEDIDO_VALIDOS
from src.database import get_db
from src.middlewares.error_handler import AppError, ValidationError
from src.models import pedido_model, produto_model
from src.services import notification_service


def criar(dados):
    if not dados:
        raise ValidationError("Dados inválidos")

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not itens or len(itens) == 0:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    db = get_db()
    try:
        total = 0
        produtos = {}
        for item in itens:
            produto = produto_model.get_by_id(db, item["produto_id"])
            if produto is None:
                raise ValidationError(
                    "Produto " + str(item["produto_id"]) + " não encontrado"
                )
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError("Estoque insuficiente para " + produto["nome"])
            produtos[item["produto_id"]] = produto
            total += produto["preco"] * item["quantidade"]

        pedido_id = pedido_model.create(db, usuario_id, total, STATUS_PEDIDO_INICIAL)
        for item in itens:
            produto = produtos[item["produto_id"]]
            pedido_model.add_item(
                db, pedido_id, item["produto_id"], item["quantidade"], produto["preco"]
            )
            produto_model.decrement_stock(db, item["produto_id"], item["quantidade"])

        db.commit()
    except Exception:
        db.rollback()
        raise

    notification_service.pedido_criado(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}


def listar_por_usuario(usuario_id):
    return pedido_model.get_by_usuario(get_db(), usuario_id)


def listar_todos():
    return pedido_model.get_all(get_db())


def atualizar_status(pedido_id, dados):
    if not dados:
        raise ValidationError("Status inválido")

    novo_status = dados.get("status", "")
    if novo_status not in STATUS_PEDIDO_VALIDOS:
        raise ValidationError("Status inválido")

    db = get_db()
    pedido_model.update_status(db, pedido_id, novo_status)
    db.commit()

    notification_service.pedido_status_alterado(pedido_id, novo_status)
