import streamlit as st
from models.pedido_venda import listar_pedidos_venda
import pandas as pd
import datetime

def pagina_relatorios():
    st.title("Relatórios de Orçamentos e Vendas")
    pedidos = listar_pedidos_venda()
    if not pedidos:
        st.info("Nenhum pedido encontrado.")
        return

    # Converter para DataFrame
    colunas = [
        "ID", "ID Cliente", "Nome Peça", "Tempo Impressão (h)", "Custo/Hora", "Filamentos Utilizados", "Preço Arquivo",
        "Margem Lucro", "Preço Custo Total", "Preço Venda", "Data Venda", "Status", "Observação"
    ]
    df = pd.DataFrame(pedidos, columns=colunas)
    df["Data Venda"] = pd.to_datetime(df["Data Venda"])

    # Filtro por período
    st.subheader("Filtrar por período")
    data_ini = st.date_input("Data inicial", value=df["Data Venda"].min().date())
    data_fim = st.date_input("Data final", value=df["Data Venda"].max().date())
    df_filtrado = df[(df["Data Venda"] >= pd.to_datetime(data_ini)) & (df["Data Venda"] <= pd.to_datetime(data_fim))]

    # Filtro por status
    status_opcao = st.selectbox("Status", options=["Todos"] + sorted(df["Status"].unique().tolist()))
    if status_opcao != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Status"] == status_opcao]

    st.subheader("Resumo")
    st.write(f"Total de pedidos: {len(df_filtrado)}")
    st.write(f"Total vendido: R$ {df_filtrado['Preço Venda'].sum():.2f}")
    st.write(f"Total de orçamentos: {len(df_filtrado[df_filtrado['Status'] == 'Orçamento Solicitado'])}")

    st.subheader("Tabela de Pedidos")
    st.dataframe(df_filtrado)

    # Exportar para CSV
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Exportar para CSV",
        data=csv,
        file_name=f"relatorio_pedidos_{data_ini}_{data_fim}.csv",
        mime='text/csv',
    ) 