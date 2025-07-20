import sqlite3

def get_connection():
    return sqlite3.connect("impressao3d.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        whatsapp TEXT,
        email TEXT,
        observacao TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS filamentos (
        id_filamento INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        cor TEXT NOT NULL,
        marca TEXT NOT NULL,
        preco_kg REAL NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos_compra (
        id_pedido_compra INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_pedido_interno TEXT NOT NULL,
        numero_pedido_fornecedor TEXT,
        data_compra TEXT NOT NULL,
        status TEXT NOT NULL,
        itens_filamento TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        id_estoque INTEGER PRIMARY KEY AUTOINCREMENT,
        id_filamento INTEGER NOT NULL,
        quantidade_kg_atual REAL NOT NULL,
        quantidade_minima_alerta_kg REAL NOT NULL,
        data_ultima_atualizacao TEXT NOT NULL,
        FOREIGN KEY (id_filamento) REFERENCES filamentos(id_filamento)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos_venda (
        id_pedido_venda INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente INTEGER NOT NULL,
        nome_peca TEXT NOT NULL,
        tempo_impressao_horas REAL NOT NULL,
        custo_impressao_hora REAL NOT NULL,
        filamentos_utilizados TEXT NOT NULL,
        preco_arquivo REAL,
        margem_lucro_percentual REAL NOT NULL,
        preco_custo_total REAL NOT NULL,
        preco_venda REAL NOT NULL,
        data_venda TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
    )
    """)
    conn.commit()
    conn.close() 