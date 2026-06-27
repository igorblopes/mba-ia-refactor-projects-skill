"""Health check operacional — contagens via models, sem expor segredos (AP-02)."""
from src.config.settings import settings
from src.database import get_db
from src.models import pedido_model, produto_model, usuario_model


def status():
    db = get_db()
    return {
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": produto_model.count(db),
            "usuarios": usuario_model.count(db),
            "pedidos": pedido_model.count(db),
        },
        "versao": settings.VERSION,
    }
