from database import get_connection

def adicionar_filamento(tipo, cor, marca, preco_kg):
    if not tipo or not cor or not marca:
        raise ValueError("Tipo, cor e marca são obrigatórios.")
    if preco_kg is None or preco_kg <= 0:
        raise ValueError("Preço por kg deve ser positivo.")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO filamentos (tipo, cor, marca, preco_kg)
        VALUES (?, ?, ?, ?)
    """, (tipo, cor, marca, preco_kg))
    conn.commit()
    conn.close()

def listar_filamentos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM filamentos")
    filamentos = cursor.fetchall()
    conn.close()
    return filamentos

def buscar_filamento(tipo=None, cor=None, marca=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM filamentos WHERE 1=1"
    params = []
    if tipo:
        query += " AND tipo LIKE ?"
        params.append(f"%{tipo}%")
    if cor:
        query += " AND cor LIKE ?"
        params.append(f"%{cor}%")
    if marca:
        query += " AND marca LIKE ?"
        params.append(f"%{marca}%")
    cursor.execute(query, params)
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def editar_filamento(id_filamento, tipo, cor, marca, preco_kg):
    if not tipo or not cor or not marca:
        raise ValueError("Tipo, cor e marca são obrigatórios.")
    if preco_kg is None or preco_kg <= 0:
        raise ValueError("Preço por kg deve ser positivo.")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE filamentos
        SET tipo = ?, cor = ?, marca = ?, preco_kg = ?
        WHERE id_filamento = ?
    """, (tipo, cor, marca, preco_kg, id_filamento))
    conn.commit()
    conn.close() 