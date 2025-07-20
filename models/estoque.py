from database import get_connection
import datetime

def entrada_filamento(id_filamento, quantidade_kg):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estoque WHERE id_filamento = ?", (id_filamento,))
    row = cursor.fetchone()
    data_atual = datetime.datetime.now().isoformat()
    if row:
        nova_qtd = row[2] + quantidade_kg
        cursor.execute("""
            UPDATE estoque
            SET quantidade_kg_atual = ?, data_ultima_atualizacao = ?
            WHERE id_filamento = ?
        """, (nova_qtd, data_atual, id_filamento))
    else:
        cursor.execute("""
            INSERT INTO estoque (id_filamento, quantidade_kg_atual, quantidade_minima_alerta_kg, data_ultima_atualizacao)
            VALUES (?, ?, ?, ?)
        """, (id_filamento, quantidade_kg, 0, data_atual))
    conn.commit()
    conn.close()

def saida_filamento(id_filamento, quantidade_kg):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estoque WHERE id_filamento = ?", (id_filamento,))
    row = cursor.fetchone()
    if row and row[2] >= quantidade_kg:
        nova_qtd = row[2] - quantidade_kg
        data_atual = datetime.datetime.now().isoformat()
        cursor.execute("""
            UPDATE estoque
            SET quantidade_kg_atual = ?, data_ultima_atualizacao = ?
            WHERE id_filamento = ?
        """, (nova_qtd, data_atual, id_filamento))
        conn.commit()
    conn.close()

def listar_estoque():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estoque")
    estoque = cursor.fetchall()
    conn.close()
    return estoque

def ajustar_minimo(id_filamento, novo_minimo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE estoque
        SET quantidade_minima_alerta_kg = ?
        WHERE id_filamento = ?
    """, (novo_minimo, id_filamento))
    conn.commit()
    conn.close() 