"""Acesso a dados de pedidos e seus itens. SQL parametrizado; sem regra de negócio."""


def create(db, usuario_id, total, status):
    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, status, total),
    )
    return cursor.lastrowid


def add_item(db, pedido_id, produto_id, quantidade, preco_unitario):
    db.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
        "VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario),
    )


def update_status(db, pedido_id, status):
    db.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id)
    )


def get_by_usuario(db, usuario_id):
    rows = db.execute(
        "SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)
    ).fetchall()
    return _build_pedidos(db, rows)


def get_all(db):
    rows = db.execute("SELECT * FROM pedidos").fetchall()
    return _build_pedidos(db, rows)


def count(db):
    return db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]


def sales_stats(db):
    """Agregação bruta de vendas (sem política de desconto — isso é do controller)."""
    row = db.execute(
        """
        SELECT
            COUNT(*)                                            AS total_pedidos,
            COALESCE(SUM(total), 0)                             AS faturamento,
            SUM(CASE WHEN status = 'pendente'  THEN 1 ELSE 0 END) AS pendentes,
            SUM(CASE WHEN status = 'aprovado'  THEN 1 ELSE 0 END) AS aprovados,
            SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS cancelados
        FROM pedidos
        """
    ).fetchone()
    return {
        "total_pedidos": row["total_pedidos"],
        "faturamento": row["faturamento"] or 0,
        "pendentes": row["pendentes"] or 0,
        "aprovados": row["aprovados"] or 0,
        "cancelados": row["cancelados"] or 0,
    }


def _build_pedidos(db, pedido_rows):
    """Monta pedidos com seus itens em 2 queries no total (resolve o N+1, AP-12)."""
    pedidos = [
        {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": [],
        }
        for row in pedido_rows
    ]
    if not pedidos:
        return pedidos

    por_id = {p["id"]: p for p in pedidos}
    placeholders = ",".join("?" * len(por_id))
    itens = db.execute(
        "SELECT ip.pedido_id, ip.produto_id, pr.nome AS produto_nome, "
        "ip.quantidade, ip.preco_unitario "
        "FROM itens_pedido ip "
        "LEFT JOIN produtos pr ON pr.id = ip.produto_id "
        f"WHERE ip.pedido_id IN ({placeholders})",
        list(por_id.keys()),
    ).fetchall()

    for item in itens:
        por_id[item["pedido_id"]]["itens"].append({
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"] or "Desconhecido",
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })
    return pedidos
