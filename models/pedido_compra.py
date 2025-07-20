from database import get_connection
import datetime
import json

def adicionar_pedido_compra(numero_pedido_interno, numero_pedido_fornecedor, data_compra, status, itens_filamento):
    if not numero_pedido_interno or not data_compra or not status:
        raise ValueError("Número interno, data e status são obrigatórios.")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pedidos_compra (numero_pedido_interno, numero_pedido_fornecedor, data_compra, status, itens_filamento)
        VALUES (?, ?, ?, ?, ?)
    """, (numero_pedido_interno, numero_pedido_fornecedor, data_compra, status, json.dumps(itens_filamento)))
    conn.commit()
    conn.close()

def listar_pedidos_compra():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos_compra")
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

def editar_status_pedido_compra(id_pedido_compra, novo_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE pedidos_compra
        SET status = ?
        WHERE id_pedido_compra = ?
    """, (novo_status, id_pedido_compra))
    conn.commit()
    conn.close() 