"""Constantes de domínio — substituem magic numbers/strings espalhados (AP-18)."""

CATEGORIAS_VALIDAS = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
]
CATEGORIA_PADRAO = "geral"

STATUS_PEDIDO_VALIDOS = [
    "pendente",
    "aprovado",
    "enviado",
    "entregue",
    "cancelado",
]
STATUS_PEDIDO_INICIAL = "pendente"

NOME_MIN = 2
NOME_MAX = 200

# Faixas de desconto sobre o faturamento bruto (limiar, taxa).
# Ordenadas do maior para o menor; aplica-se a primeira que o faturamento ultrapassa.
DISCOUNT_TIERS = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]
