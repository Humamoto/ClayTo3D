import streamlit as st
from ui.calculadora_cliente import pagina_calculadora_cliente

st.set_page_config(page_title="Orçamento ClayTo3D", page_icon=":cube:", layout="centered")

# Logo e título
st.image("logo.png", use_container_width=True)
st.markdown("<h1 style='text-align:center; margin-top:0;'>Orçamento ClayTo3D</h1>", unsafe_allow_html=True)

pagina_calculadora_cliente()