import streamlit as st
from models.pedido_compra import adicionar_pedido_compra, listar_pedidos_compra, editar_status_pedido_compra
import datetime
import json

def pagina_pedidos_compra():
    st.title("Pedidos de Compra de Filamento")

    with st.form("form_pedido_compra"):
        numero_pedido_interno = st.text_input("Número do Pedido Interno*")
        numero_pedido_fornecedor = st.text_input("Número do Pedido do Fornecedor")
        data_compra = st.date_input("Data da Compra", value=datetime.date.today())
        status = st.selectbox("Status", ["Pendente", "Recebido", "Cancelado"])
        itens_filamento = st.text_area("Itens de Filamento (JSON: lista de dicionários com id_filamento, quantidade_kg, preco_unitario_compra_kg)")
        submitted = st.form_submit_button("Adicionar Pedido de Compra")
        if submitted:
            try:
                itens = json.loads(itens_filamento) if itens_filamento else []
                adicionar_pedido_compra(numero_pedido_interno, numero_pedido_fornecedor, str(data_compra), status, itens)
                st.success("Pedido de compra adicionado!")
            except Exception as e:
                st.error(str(e))

    st.subheader("Lista de Pedidos de Compra")
    pedidos = listar_pedidos_compra()
    for p in pedidos:
        st.write(f"ID: {p[0]} | Interno: {p[1]} | Fornecedor: {p[2]} | Data: {p[3]} | Status: {p[4]}")
        if st.button(f"Editar Status {p[0]}", key=f"edit_status_{p[0]}"):
            novo_status = st.selectbox("Novo Status", ["Pendente", "Recebido", "Cancelado"], key=f"status_{p[0]}")
            if st.button("Salvar Status", key=f"save_status_{p[0]}"):
                try:
                    editar_status_pedido_compra(p[0], novo_status)
                    st.success("Status atualizado!")
                except Exception as e:
                    st.error(str(e)) 