import streamlit as st
from models.pedido_venda import adicionar_pedido_venda, listar_pedidos_venda, editar_pedido_venda
import datetime
import json

def pagina_pedidos_venda():
    st.title("Pedidos de Venda")

    # Alerta visual para orçamentos pendentes
    pedidos = listar_pedidos_venda()
    orcamentos_pendentes = [p for p in pedidos if p[11] == "Orçamento Solicitado"]
    if orcamentos_pendentes:
        ids = ', '.join(str(p[0]) for p in orcamentos_pendentes)
        st.warning(f"Há {len(orcamentos_pendentes)} orçamento(s) pendente(s): ID(s) {ids}")

    with st.form("form_pedido_venda"):
        id_cliente = st.number_input("ID do Cliente*", min_value=1, step=1)
        nome_peca = st.text_input("Nome da Peça*")
        tempo_impressao_horas = st.number_input("Tempo de Impressão (horas)*", min_value=0.0, step=0.1)
        custo_impressao_hora = st.number_input("Custo de Impressão por Hora*", min_value=0.0, step=0.01)
        filamentos_utilizados = st.text_area("Filamentos Utilizados (JSON: lista de dicionários com id_filamento, quantidade_g_utilizada, preco_kg)")
        preco_arquivo = st.number_input("Preço do Arquivo", min_value=0.0, step=0.01)
        margem_lucro_percentual = st.number_input("Margem de Lucro (ex: 1.5 para 50%)*", min_value=1.0, step=0.01, value=1.5)
        data_venda = st.date_input("Data da Venda", value=datetime.date.today())
        status = st.selectbox("Status", ["Em Produção", "Concluído", "Entregue", "Cancelado"])
        submitted = st.form_submit_button("Adicionar Pedido de Venda")
        if submitted:
            try:
                filamentos = json.loads(filamentos_utilizados) if filamentos_utilizados else []
                adicionar_pedido_venda(id_cliente, nome_peca, tempo_impressao_horas, custo_impressao_hora, filamentos, preco_arquivo, margem_lucro_percentual, str(data_venda), status)
                st.success("Pedido de venda adicionado!")
            except Exception as e:
                st.error(str(e))

    st.subheader("Lista de Pedidos de Venda")
    for p in pedidos:
        st.write(f"ID: {p[0]} | Cliente: {p[1]} | Peça: {p[2]} | Data: {p[9]} | Status: {p[11]}")
        if st.button(f"Editar Status {p[0]}", key=f"edit_status_venda_{p[0]}"):
            novo_status = st.selectbox("Novo Status", ["Em Produção", "Concluído", "Entregue", "Cancelado"], key=f"status_venda_{p[0]}")
            if st.button("Salvar Status", key=f"save_status_venda_{p[0]}"):
                try:
                    editar_pedido_venda(p[0], novo_status)
                    st.success("Status atualizado!")
                except Exception as e:
                    st.error(str(e)) 