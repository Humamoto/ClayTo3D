from database import get_connection
import re

def validar_email(email):
    if not email:
        return True
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def adicionar_cliente(nome, whatsapp, email, observacao):
    if not nome:
        raise ValueError("Nome é obrigatório.")
    if email and not validar_email(email):
        raise ValueError("Email inválido.")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clientes (nome, whatsapp, email, observacao)
        VALUES (?, ?, ?, ?)
    """, (nome, whatsapp, email, observacao))
    conn.commit()
    conn.close()

def listar_clientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

def buscar_cliente_por_nome_ou_id(termo):
    conn = get_connection()
    cursor = conn.cursor()
    if termo.isdigit():
        cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (int(termo),))
    else:
        cursor.execute("SELECT * FROM clientes WHERE nome LIKE ?", (f"%{termo}%",))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def editar_cliente(id_cliente, nome, whatsapp, email, observacao):
    if not nome:
        raise ValueError("Nome é obrigatório.")
    if email and not validar_email(email):
        raise ValueError("Email inválido.")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clientes
        SET nome = ?, whatsapp = ?, email = ?, observacao = ?
        WHERE id_cliente = ?
    """, (nome, whatsapp, email, observacao, id_cliente))
    conn.commit()
    conn.close() 