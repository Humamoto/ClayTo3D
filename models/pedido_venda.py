from database import get_connection
import datetime
import json

def adicionar_pedido_venda(id_cliente, nome_peca, tempo_impressao_horas, custo_impressao_hora, filamentos_utilizados, preco_arquivo, margem_lucro_percentual, data_venda, status, observacao=None):
    preco_custo_total = custo_impressao_hora * tempo_impressao_horas + sum([f['preco_kg'] * f['quantidade_g_utilizada']/1000 for f in filamentos_utilizados]) + preco_arquivo
    preco_venda = preco_custo_total * margem_lucro_percentual
    conn = get_connection()
    cursor = conn.cursor()
    if observacao is not None:
        cursor.execute("""
            INSERT INTO pedidos_venda (id_cliente, nome_peca, tempo_impressao_horas, custo_impressao_hora, filamentos_utilizados, preco_arquivo, margem_lucro_percentual, preco_custo_total, preco_venda, data_venda, status, observacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_cliente, nome_peca, tempo_impressao_horas, custo_impressao_hora, json.dumps(filamentos_utilizados), preco_arquivo, margem_lucro_percentual, preco_custo_total, preco_venda, data_venda, status, observacao))
    else:
        cursor.execute("""
            INSERT INTO pedidos_venda (id_cliente, nome_peca, tempo_impressao_horas, custo_impressao_hora, filamentos_utilizados, preco_arquivo, margem_lucro_percentual, preco_custo_total, preco_venda, data_venda, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_cliente, nome_peca, tempo_impressao_horas, custo_impressao_hora, json.dumps(filamentos_utilizados), preco_arquivo, margem_lucro_percentual, preco_custo_total, preco_venda, data_venda, status))
    conn.commit()
    conn.close()

def listar_pedidos_venda():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos_venda")
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

def editar_pedido_venda(id_pedido_venda, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE pedidos_venda
        SET status = ?
        WHERE id_pedido_venda = ?
    """, (status, id_pedido_venda))
    conn.commit()
    conn.close() 