import streamlit as st
from models.filamento import adicionar_filamento, listar_filamentos, buscar_filamento, editar_filamento

def pagina_filamentos():
    st.title("Cadastro de Filamentos")

    with st.form("form_filamento"):
        tipo = st.text_input("Tipo* (ex: PLA, PETG)")
        cor = st.text_input("Cor*")
        marca = st.text_input("Marca*")
        preco_kg = st.number_input("Preço por kg*", min_value=0.0, step=0.01, format="%.2f")
        submitted = st.form_submit_button("Adicionar Filamento")
        if submitted:
            try:
                adicionar_filamento(tipo, cor, marca, preco_kg)
                st.success("Filamento adicionado com sucesso!")
            except Exception as e:
                st.error(str(e))

    st.subheader("Buscar Filamento")
    tipo_busca = st.text_input("Tipo")
    cor_busca = st.text_input("Cor")
    marca_busca = st.text_input("Marca")
    if tipo_busca or cor_busca or marca_busca:
        filamentos = buscar_filamento(tipo_busca, cor_busca, marca_busca)
    else:
        filamentos = listar_filamentos()

    st.subheader("Lista de Filamentos")
    for f in filamentos:
        st.write(f"ID: {f[0]} | Tipo: {f[1]} | Cor: {f[2]} | Marca: {f[3]} | Preço/kg: R$ {f[4]:.2f}")
        if st.button(f"Editar {f[0]}", key=f"edit_fil_{f[0]}"):
            novo_tipo = st.text_input("Tipo", value=f[1], key=f"tipo_{f[0]}")
            nova_cor = st.text_input("Cor", value=f[2], key=f"cor_{f[0]}")
            nova_marca = st.text_input("Marca", value=f[3], key=f"marca_{f[0]}")
            novo_preco = st.number_input("Preço por kg", value=f[4], min_value=0.0, step=0.01, format="%.2f", key=f"preco_{f[0]}")
            if st.button("Salvar", key=f"save_fil_{f[0]}"):
                try:
                    editar_filamento(f[0], novo_tipo, nova_cor, nova_marca, novo_preco)
                    st.success("Filamento atualizado!")
                except Exception as e:
                    st.error(str(e)) 