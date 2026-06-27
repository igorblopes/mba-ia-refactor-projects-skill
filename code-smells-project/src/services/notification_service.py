"""Efeitos colaterais de notificação isolados da regra de negócio (AP-10).

Os controllers chamam esta interface; os canais (email/SMS/push) podem mudar sem
tocar na lógica de pedidos, e a regra fica testável sem disparar notificações.
"""
import logging

logger = logging.getLogger(__name__)


def pedido_criado(pedido_id, usuario_id):
    logger.info("EMAIL: Pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("SMS: Seu pedido foi recebido!")
    logger.info("PUSH: Novo pedido recebido pelo sistema")


def pedido_status_alterado(pedido_id, status):
    if status == "aprovado":
        logger.info("NOTIFICAÇÃO: Pedido %s foi aprovado! Preparar envio.", pedido_id)
    elif status == "cancelado":
        logger.info("NOTIFICAÇÃO: Pedido %s cancelado. Devolver estoque.", pedido_id)
