"""Utilitário de tempo.

`datetime.utcnow()` está deprecated no Python 3.12. Centralizamos a obtenção do
"agora" em UTC aqui. Retornamos um datetime *naive* (sem tzinfo) para manter
compatibilidade com as colunas `DateTime` do banco e com datas parseadas via
`strptime`, evitando comparações entre datetimes aware e naive.
"""
from datetime import datetime, timezone


def utcnow():
    """Timestamp UTC naive — substituto seguro para `datetime.utcnow()`."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
