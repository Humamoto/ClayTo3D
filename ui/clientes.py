import streamlit as st
from models.cliente import adicionar_cliente, listar_clientes, buscar_cliente_por_nome_ou_id, editar_cliente

def pagina_clientes():
    st.title("Cadastro de Clientes")

    with st.form("form_cliente"):
        nome = st.text_input("Nome*", max_chars=100)
        whatsapp = st.text_input("WhatsApp")
        email = st.text_input("Email")
        observacao = st.text_area("Observação")
        submitted = st.form_submit_button("Adicionar Cliente")
        if submitted:
            try:
                adicionar_cliente(nome, whatsapp, email, observacao)
                st.success("Cliente adicionado com sucesso!")
            except Exception as e:
                st.error(str(e))

    st.subheader("Buscar Cliente")
    termo_busca = st.text_input("Nome ou ID")
    if termo_busca:
        clientes = buscar_cliente_por_nome_ou_id(termo_busca)
    else:
        clientes = listar_clientes()

    st.subheader("Lista de Clientes")
    for c in clientes:
        st.write(f"ID: {c[0]} | Nome: {c[1]} | WhatsApp: {c[2]} | Email: {c[3]}")
        if st.button(f"Editar {c[0]}", key=f"edit_{c[0]}"):
            novo_nome = st.text_input("Nome", value=c[1], key=f"nome_{c[0]}")
            novo_whatsapp = st.text_input("WhatsApp", value=c[2], key=f"whatsapp_{c[0]}")
            novo_email = st.text_input("Email", value=c[3], key=f"email_{c[0]}")
            nova_obs = st.text_area("Observação", value=c[4], key=f"obs_{c[0]}")
            if st.button("Salvar", key=f"save_{c[0]}"):
                try:
                    editar_cliente(c[0], novo_nome, novo_whatsapp, novo_email, nova_obs)
                    st.success("Cliente atualizado!")
                except Exception as e:
                    st.error(str(e)) 