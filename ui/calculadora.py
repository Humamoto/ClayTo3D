import streamlit as st
from models.filamento import listar_filamentos
import datetime
import json
import os

CONFIG_FILE = "config.json"

def carregar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"custo_impressao_hora": 10.0, "margem_lucro_percentual": 1.5}

def salvar_config(custo, margem):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"custo_impressao_hora": custo, "margem_lucro_percentual": margem}, f)

def pagina_calculadora():
    st.title("Calculadora de Orçamento para Cliente (Admin)")
    st.write("Simule o custo e o preço de venda de uma peça impressa em 3D.")

    # Carregar config persistente
    config = carregar_config()
    if 'custo_impressao_hora' not in st.session_state:
        st.session_state.custo_impressao_hora = config["custo_impressao_hora"]
    if 'margem_lucro_percentual' not in st.session_state:
        st.session_state.margem_lucro_percentual = config["margem_lucro_percentual"]

    with st.expander("Parâmetros do Orçamento (Admin)", expanded=True):
        novo_custo = st.number_input(
            "Custo de Impressão por Hora (R$)", min_value=0.0, step=0.01, value=st.session_state.custo_impressao_hora, format="%.2f", key="custo_admin")
        nova_margem = st.number_input(
            "Margem de Lucro (ex: 1.5 para 50%)", min_value=1.0, step=0.01, value=st.session_state.margem_lucro_percentual, key="margem_admin")
        if novo_custo != st.session_state.custo_impressao_hora or nova_margem != st.session_state.margem_lucro_percentual:
            st.session_state.custo_impressao_hora = novo_custo
            st.session_state.margem_lucro_percentual = nova_margem
            salvar_config(novo_custo, nova_margem)
            st.success("Configuração salva!")

    with st.form("form_calculadora"):
        nome_peca = st.text_input("Nome da Peça (opcional)")
        tempo_impressao_horas = st.number_input("Tempo de Impressão (horas)*", min_value=0.0, step=0.1)
        filamentos = listar_filamentos()
        opcoes_filamento = {f"{f[1]} - {f[2]} - {f[3]} (R$ {f[4]:.2f}/kg)": f for f in filamentos}
        filamento_escolhido = st.selectbox("Filamento*", list(opcoes_filamento.keys())) if opcoes_filamento else None
        quantidade_g_utilizada = st.number_input("Quantidade de Filamento Utilizada (g)*", min_value=0.0, step=1.0)
        preco_arquivo = st.number_input("Preço do Arquivo (opcional)", min_value=0.0, step=0.01, value=0.0)
        submitted = st.form_submit_button("Calcular Orçamento")

    if submitted and filamento_escolhido:
        f = opcoes_filamento[filamento_escolhido]
        preco_kg = f[4]
        custo_filamento = preco_kg * (quantidade_g_utilizada / 1000)
        preco_custo_total = st.session_state.custo_impressao_hora * tempo_impressao_horas + custo_filamento + preco_arquivo
        preco_venda = preco_custo_total * st.session_state.margem_lucro_percentual
        st.success("Orçamento Gerado!")
        st.write(f"**Custo Total:** R$ {preco_custo_total:.2f}")
        st.write(f"**Preço de Venda Sugerido:** R$ {preco_venda:.2f}")
        with st.expander("Detalhamento do cálculo"):
            st.write(f"Tempo de Impressão: {tempo_impressao_horas} h x R$ {st.session_state.custo_impressao_hora:.2f}/h = R$ {st.session_state.custo_impressao_hora * tempo_impressao_horas:.2f}")
            st.write(f"Filamento: {quantidade_g_utilizada} g x R$ {preco_kg:.2f}/kg = R$ {custo_filamento:.2f}")
            st.write(f"Preço do Arquivo: R$ {preco_arquivo:.2f}")
            st.write(f"Margem de Lucro: {((st.session_state.margem_lucro_percentual-1)*100):.0f}%")
    elif submitted:
        st.error("Selecione um filamento para simular o orçamento.") 