import streamlit as st
import os
import importlib.util
from models.pedido_venda import adicionar_pedido_venda
import urllib.parse
import datetime
import os as _os
import socket

# Google Sheets integração
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
except ImportError:
    gspread = None
    ServiceAccountCredentials = None

def enviar_pedido_google_sheets(dados):
    nome_planilha = "Pedidos_ClayTo3D"
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])

    try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            sheet = client.open(nome_planilha).sheet1
            sheet.append_row(dados)
    except Exception as e:
        st.error(f"Erro ao salvar no Google Sheets: {e}")


# Detecta ambiente público automaticamente
def is_public_env():
    host = socket.gethostname().lower()
    if "streamlit" in host or "cloud" in host:
        return True
    if os.environ.get("CLAYTO3D_PUBLIC", "0") == "1":
        return True
    return False

IS_PUBLIC = True # Mantido como estava no seu código

# Função para decidir se usa lista fixa ou banco
def listar_filamentos():
    filamentos_publicos_path = _os.path.join(_os.path.dirname(__file__), "filamentos_publicos.py")
    if _os.path.exists(filamentos_publicos_path):
        spec = importlib.util.spec_from_file_location("filamentos_publicos", filamentos_publicos_path)
        filamentos_publicos = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(filamentos_publicos)
        return getattr(filamentos_publicos, "FILAMENTOS_PUBLICOS", [])
    else:
        from models.filamento import listar_filamentos as lf
        return lf()

def pagina_calculadora_cliente():
    st.title("Simule seu Orçamento 3D")
    st.write("Preencha os dados abaixo para estimar o valor da sua impressão 3D.")
    st.info("O valor apresentado é uma estimativa. O valor final pode variar após análise do projeto.")

    if 'orcamento' not in st.session_state:
        st.session_state.orcamento = None
    if 'whatsapp_link' not in st.session_state:
        st.session_state.whatsapp_link = None
    if 'orcamento_registrado' not in st.session_state:
        st.session_state.orcamento_registrado = False
    if 'filamentos_lista' not in st.session_state:
        st.session_state.filamentos_lista = []

    nome_cliente = st.text_input("Seu nome*")
    telefone_cliente = st.text_input("Seu WhatsApp* (apenas números)")
    nome_peca = st.text_input("Nome da Peça (opcional)")
    tempo_impressao = st.number_input("Tempo de Impressão (horas)*", min_value=0.0, step=0.1)
    filamentos = listar_filamentos()
    opcoes = {f"{f[1]} - {f[2]} - {f[3]} (R$ {f[4]:.2f}/kg)": f for f in filamentos}
    filamento_escolhido = st.selectbox("Filamento*", list(opcoes.keys())) if opcoes else None
    quantidade_g = st.number_input("Quantidade de Filamento (g)*", min_value=0.0, step=1.0, key="qtd_filamento")

    if st.button("Adicionar filamento") and filamento_escolhido and quantidade_g > 0:
        f = opcoes[filamento_escolhido]
        st.session_state.filamentos_lista.append({
            'id_filamento': f[0],
            'descricao': filamento_escolhido,
            'quantidade_g_utilizada': quantidade_g,
            'preco_kg': f[4]
        })
        st.success(f"Filamento adicionado: {filamento_escolhido} - {quantidade_g}g")

    if st.session_state.filamentos_lista:
        st.markdown("**Filamentos adicionados:**")
        for i, fil in enumerate(st.session_state.filamentos_lista):
            st.write(f"{i+1}. {fil['descricao']} - {fil['quantidade_g_utilizada']}g")
        if st.button("Limpar filamentos"):
            st.session_state.filamentos_lista = []

    st.markdown("**Anexos (opcional):**")
    arquivo_stl = st.file_uploader("Arquivo STL", type=["stl"])
    imagens = st.file_uploader("Imagens (JPG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    link_extra = st.text_input("Link extra (ex: Google Drive, WeTransfer, etc)")

    calcular = st.button("Calcular orçamento")

    if calcular and nome_cliente and telefone_cliente and st.session_state.filamentos_lista:
        custo_hora = 10.0
        margem = 1.5
        preco_custo_filamentos = sum([fil['preco_kg'] * (fil['quantidade_g_utilizada']/1000) for fil in st.session_state.filamentos_lista])
        preco_custo = custo_hora * tempo_impressao + preco_custo_filamentos
        preco_venda = preco_custo * margem
        # Salvar arquivos enviados
        anexos_info = []
        pasta_anexos = "anexos_orcamento"
        os.makedirs(pasta_anexos, exist_ok=True)
        if arquivo_stl:
            stl_path = os.path.join(pasta_anexos, f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{arquivo_stl.name}")
            with open(stl_path, "wb") as f:
                f.write(arquivo_stl.getbuffer())
            anexos_info.append(f"STL: {stl_path}")
        if imagens:
            for img in imagens:
                img_path = os.path.join(pasta_anexos, f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{img.name}")
                with open(img_path, "wb") as f:
                    f.write(img.getbuffer())
                anexos_info.append(f"Imagem: {img_path}")
        if link_extra:
            anexos_info.append(f"Link: {link_extra}")
        st.session_state.orcamento = {
            'nome_cliente': nome_cliente,
            'telefone_cliente': telefone_cliente,
            'nome_peca': nome_peca,
            'tempo_impressao': tempo_impressao,
            'filamentos_utilizados': st.session_state.filamentos_lista.copy(),
            'preco_venda': preco_venda,
            'custo_hora': custo_hora,
            'margem': margem,
            'anexos': anexos_info
        }
        st.session_state.orcamento_registrado = False
        st.session_state.whatsapp_link = None
    elif calcular and (not nome_cliente or not telefone_cliente):
        st.warning("Por favor, preencha seu nome e WhatsApp para prosseguir.")
    elif calcular and not st.session_state.filamentos_lista:
        st.warning("Adicione pelo menos um filamento para calcular o orçamento.")

    if st.session_state.orcamento:
        preco_venda = st.session_state.orcamento['preco_venda']
        st.success(f"Valor estimado: R$ {preco_venda:.2f}")
        st.caption("Este valor é uma estimativa. O valor final pode variar após análise do projeto.")

        if st.button("Solicitar orçamento"):
            if IS_PUBLIC:
                # Salva no Google Sheets
                dados = [
                    st.session_state.orcamento['nome_cliente'],
                    st.session_state.orcamento['telefone_cliente'],
                    st.session_state.orcamento['nome_peca'],
                    st.session_state.orcamento['tempo_impressao'],
                    "; ".join([f"{fil['descricao']} - {fil['quantidade_g_utilizada']}g" for fil in st.session_state.orcamento['filamentos_utilizados']]),
                    f"R$ {st.session_state.orcamento['preco_venda']:.2f}",
                    str(datetime.date.today()),
                    next((a for a in st.session_state.orcamento['anexos'] if a.startswith('STL:')), ''),
                    "; ".join([a for a in st.session_state.orcamento['anexos'] if a.startswith('Imagem:')]),
                    next((a.replace('Link: ', '') for a in st.session_state.orcamento['anexos'] if a.startswith('Link:')), '')
                ]
                try:
                    enviar_pedido_google_sheets(dados)
                    st.success("Orçamento enviado para a ClayTo3D! Você pode acompanhar pelo WhatsApp.")
                except Exception as e:
                    st.error(f"Erro ao salvar no Google Sheets: {e}")
            else:
                # Registrar orçamento no sistema (admin/local)
                if not st.session_state.orcamento_registrado:
                    id_cliente = None
                    filamentos_utilizados = [
                        {
                            'id_filamento': fil['id_filamento'],
                            'quantidade_g_utilizada': fil['quantidade_g_utilizada'],
                            'preco_kg': fil['preco_kg']
                        } for fil in st.session_state.orcamento['filamentos_utilizados']
                    ]
                    try:
                        observacao = f"Nome: {st.session_state.orcamento['nome_cliente']} | WhatsApp: {st.session_state.orcamento['telefone_cliente']}"
                        if st.session_state.orcamento['anexos']:
                            observacao += " | Anexos: " + "; ".join(st.session_state.orcamento['anexos'])
                        adicionar_pedido_venda(
                            id_cliente=id_cliente,
                            nome_peca=st.session_state.orcamento['nome_peca'] or '-',
                            tempo_impressao_horas=st.session_state.orcamento['tempo_impressao'],
                            custo_impressao_hora=st.session_state.orcamento['custo_hora'],
                            filamentos_utilizados=filamentos_utilizados,
                            preco_arquivo=0.0,
                            margem_lucro_percentual=st.session_state.orcamento['margem'],
                            data_venda=str(datetime.date.today()),
                            status="Orçamento Solicitado",
                            observacao=observacao
                        )
                        st.session_state.orcamento_registrado = True
                        st.success("Orçamento registrado! Você pode acompanhar pelo admin.")
                    except Exception as e:
                        st.error(f"Erro ao registrar orçamento: {e}")
            # Gera o link do WhatsApp (sempre)
            numero_whatsapp = "5541997730248"
            mensagem = f"""Olá! Gostaria de solicitar um orçamento para impressão 3D:\n\nNome: {st.session_state.orcamento['nome_cliente']}\nWhatsApp: {st.session_state.orcamento['telefone_cliente']}\nPeça: {st.session_state.orcamento['nome_peca'] or '-'}\nTempo de impressão: {st.session_state.orcamento['tempo_impressao']} horas\n"""
            for fil in st.session_state.orcamento['filamentos_utilizados']:
                mensagem += f"Filamento: {fil['descricao']} - {fil['quantidade_g_utilizada']}g\n"
            mensagem += f"Valor estimado: R$ {st.session_state.orcamento['preco_venda']:.2f}"
            if st.session_state.orcamento['anexos']:
                mensagem += "\nAnexos: " + "; ".join(st.session_state.orcamento['anexos'])
            mensagem += "\n\nAguardo retorno!"
            mensagem_url = urllib.parse.quote(mensagem)
            st.session_state.whatsapp_link = f"https://wa.me/{numero_whatsapp}?text={mensagem_url}"

    if st.session_state.whatsapp_link:
        st.markdown(f"[Solicitar orçamento via WhatsApp]({st.session_state.whatsapp_link})", unsafe_allow_html=True)