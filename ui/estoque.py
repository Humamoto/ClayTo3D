import streamlit as st
from models.estoque import listar_estoque, ajustar_minimo

def pagina_estoque():
    st.title("Estoque de Filamentos")
    estoque = listar_estoque()
    st.subheader("Lista de Estoque")
    for e in estoque:
        st.write(f"ID Estoque: {e[0]} | ID Filamento: {e[1]} | Qtd Atual: {e[2]:.2f} kg | Mínimo Alerta: {e[3]:.2f} kg | Última Atualização: {e[4]}")
        if e[2] < e[3]:
            st.warning(f"Filamento ID {e[1]} abaixo do mínimo!")
        if st.button(f"Ajustar Mínimo {e[1]}", key=f"ajustar_min_{e[1]}"):
            novo_min = st.number_input("Novo mínimo (kg)", value=e[3], min_value=0.0, step=0.01, format="%.2f", key=f"min_{e[1]}")
            if st.button("Salvar Mínimo", key=f"save_min_{e[1]}"):
                try:
                    ajustar_minimo(e[1], novo_min)
                    st.success("Mínimo ajustado!")
                except Exception as ex:
                    st.error(str(ex)) 