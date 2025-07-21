import streamlit as st
from ui.calculadora_cliente import pagina_calculadora_cliente

st.set_page_config(page_title="Orçamento ClayTo3D", page_icon=":cube:", layout="centered")

# CSS para logo como marca d'água de fundo
st.markdown("""
    <style>
    .logo-bg {
        position: fixed;
        left: 0; top: 0; width: 100vw; height: 100vh;
        z-index: 0;
        background: url('logo.png') no-repeat center center;
        background-size: 50vw;
        opacity: 0.08;
        pointer-events: none;
    }
    /* Opcional: centralizar o título */
    .stApp > header, .stApp > .block-container { z-index: 1; }
    </style>
    <div class="logo-bg"></div>
""", unsafe_allow_html=True)

# Título centralizado
st.markdown("<h1 style='text-align:center; margin-top:0;'>Orçamento ClayTo3D</h1>", unsafe_allow_html=True)

pagina_calculadora_cliente()