import sqlite3

conn = sqlite3.connect("impressao3d.db")
cur = conn.cursor()

# Renomear tabela antiga
cur.execute("ALTER TABLE pedidos_venda RENAME TO pedidos_venda_old;")

# Criar nova tabela com id_cliente permitindo NULL
cur.execute("""
CREATE TABLE pedidos_venda (
    id_pedido_venda INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER,
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
);
""")

# Copiar dados da tabela antiga
cur.execute("""
INSERT INTO pedidos_venda (
    id_pedido_venda, id_cliente, nome_peca, tempo_impressao_horas, custo_impressao_hora,
    filamentos_utilizados, preco_arquivo, margem_lucro_percentual, preco_custo_total,
    preco_venda, data_venda, status
)
SELECT
    id_pedido_venda, id_cliente, nome_peca, tempo_impressao_horas, custo_impressao_hora,
    filamentos_utilizados, preco_arquivo, margem_lucro_percentual, preco_custo_total,
    preco_venda, data_venda, status
FROM pedidos_venda_old;
""")

# Remover tabela antiga
cur.execute("DROP TABLE pedidos_venda_old;")

conn.commit()
conn.close()

print("Migração concluída com sucesso!")