"""Acesso a dados de produtos. Apenas SQL parametrizado; sem regra de negócio."""


def _to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def get_all(db):
    rows = db.execute("SELECT * FROM produtos").fetchall()
    return [_to_dict(row) for row in rows]


def get_by_id(db, produto_id):
    row = db.execute(
        "SELECT * FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    return _to_dict(row) if row else None


def create(db, nome, descricao, preco, estoque, categoria):
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
        "VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    return cursor.lastrowid


def update(db, produto_id, nome, descricao, preco, estoque, categoria):
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, "
        "estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )


def delete(db, produto_id):
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))


def decrement_stock(db, produto_id, quantidade):
    db.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        (quantidade, produto_id),
    )


def search(db, termo=None, categoria=None, preco_min=None, preco_max=None):
    clauses, params = ["1=1"], []
    if termo:
        clauses.append("(nome LIKE ? OR descricao LIKE ?)")
        params += [f"%{termo}%", f"%{termo}%"]
    if categoria:
        clauses.append("categoria = ?")
        params.append(categoria)
    if preco_min is not None:
        clauses.append("preco >= ?")
        params.append(preco_min)
    if preco_max is not None:
        clauses.append("preco <= ?")
        params.append(preco_max)

    sql = "SELECT * FROM produtos WHERE " + " AND ".join(clauses)
    rows = db.execute(sql, params).fetchall()
    return [_to_dict(row) for row in rows]


def count(db):
    return db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
