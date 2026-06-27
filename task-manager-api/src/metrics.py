"""Cálculos de métricas compartilhados (DRY)."""


def completion_rate(done, total):
    if total > 0:
        return round((done / total) * 100, 2)
    return 0
