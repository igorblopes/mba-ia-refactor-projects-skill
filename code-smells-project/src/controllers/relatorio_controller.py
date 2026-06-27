"""Caso de uso de relatório de vendas: regra de desconto sobre dados agregados."""
from src.config.constants import DISCOUNT_TIERS
from src.database import get_db
from src.models import pedido_model


def gerar_relatorio_vendas():
    stats = pedido_model.sales_stats(get_db())
    faturamento = stats["faturamento"]
    desconto = _desconto_para(faturamento)
    total_pedidos = stats["total_pedidos"]

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": stats["pendentes"],
        "pedidos_aprovados": stats["aprovados"],
        "pedidos_cancelados": stats["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }


def _desconto_para(faturamento):
    for limiar, taxa in DISCOUNT_TIERS:
        if faturamento > limiar:
            return faturamento * taxa
    return 0
