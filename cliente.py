import streamlit as st
from ui.calculadora_cliente import pagina_calculadora_cliente

st.set_page_config(
    page_title="Orçamento ClayTo3D",
    page_icon="logo.png",  # Isso define o favicon na aba do navegador
    layout="centered"
)

# CSS para neon nos títulos
st.markdown('''
    <style>
    .stApp h1, .stApp h2, .stApp h3 {
        background: linear-gradient(90deg, #ff4ecd 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 8px #ff4ecd88;
    }
    .logo-topo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 180px;
        max-width: 40vw;
        margin-bottom: 0.5rem;
        margin-top: 1rem;
        border-radius: 16px;
        box-shadow: 0 0 24px #ff4ecd88;
    }
    </style>
''', unsafe_allow_html=True)

# Logo pequena centralizada no topo
st.markdown('<img src="logo.png" class="logo-topo">', unsafe_allow_html=True)

# Título centralizado
st.markdown("<h1 style='text-align:center; margin-top:0;'>Orçamento ClayTo3D</h1>", unsafe_allow_html=True)

pagina_calculadora_cliente()