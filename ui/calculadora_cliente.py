import streamlit as st
import os
import importlib.util
from models.pedido_venda import adicionar_pedido_venda
import urllib.parse
import datetime
import os as _os
import socket
import time
from streamlit_extras.stylable_container import stylable_container

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

    # Botão estilizado para MakerWorld
    st.markdown('''
        <div style='text-align:center; margin: 2rem 0;'>
            <a href="https://makerworld.com/pt" target="_blank" style="background: linear-gradient(90deg, #ff4ecd 0%, #7c3aed 100%); color: white; border: none; border-radius: 8px; padding: 1rem 2.5rem; font-size: 1.3rem; font-weight: bold; box-shadow: 0 0 16px #ff4ecd88; text-decoration: none; display: inline-block;">
                <img src="https://makerworld.com/favicon.ico" width="32" style="vertical-align:middle; margin-right:0.7rem;"> Explorar modelos 3D em MakerWorld
            </a>
        </div>
    ''', unsafe_allow_html=True)

    # (Removido campo de input e prévia de imagem do modelo MakerWorld)

    if 'orcamento' not in st.session_state:
        st.session_state.orcamento = None
    if 'whatsapp_link' not in st.session_state:
        st.session_state.whatsapp_link = None
    if 'orcamento_registrado' not in st.session_state:
        st.session_state.orcamento_registrado = False
    if 'filamentos_lista' not in st.session_state:
        st.session_state.filamentos_lista = []
    if 'orcamento_enviado' not in st.session_state:
        st.session_state.orcamento_enviado = False

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
    st.markdown("""
    **Como anexar arquivos ao seu orçamento:**
    - Suba seu arquivo STL e imagens em um serviço como [Google Drive](https://drive.google.com), [Dropbox](https://dropbox.com) ou [WeTransfer](https://wetransfer.com).
    - Gere um link compartilhável e cole no campo abaixo.
    """)
    link_extra = st.text_input(
        "Link para arquivos (Google Drive, Dropbox, etc)",
        placeholder="Cole aqui o link compartilhável dos seus arquivos"
    )

    # Botão Calcular Orçamento
    calcular = st.button("Calcular orçamento")

    if calcular:
        if not nome_cliente or not telefone_cliente:
            st.warning("Por favor, preencha seu nome e WhatsApp para prosseguir.")
        elif not st.session_state.filamentos_lista:
            st.warning("Adicione pelo menos um filamento para calcular o orçamento.")
        elif not link_extra:
            st.warning("Por favor, cole o link dos arquivos STL/imagens para análise do orçamento.")
        else:
            custo_hora = 10.0
            margem = 1.5
            preco_custo_filamentos = sum([fil['preco_kg'] * (fil['quantidade_g_utilizada']/1000) for fil in st.session_state.filamentos_lista])
            preco_custo = custo_hora * tempo_impressao + preco_custo_filamentos
            preco_venda = preco_custo * margem

            anexos_info = []
            pasta_anexos = "anexos_orcamento"
            _os.makedirs(pasta_anexos, exist_ok=True)
            # Não salva mais arquivos locais, só usa o link
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
            st.session_state.whatsapp_link_gerado = None
            st.session_state.orcamento_registrado = False

    if st.session_state.orcamento:
        preco_venda = st.session_state.orcamento['preco_venda']
        valor_formatado = f"{preco_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        filamentos_html = "<br>".join([f"{fil['descricao']} - {fil['quantidade_g_utilizada']}g" for fil in st.session_state.orcamento['filamentos_utilizados']])
        st.markdown(f"""
    <div style='background: #23243a; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 0 16px #7c3aed44;'>
        <h3 style='text-align:center; margin-bottom:1.2rem;'>Resumo do Orçamento</h3>
        <table style='width:100%; font-size:1.1rem; color:#fff;'>
            <tr><td><b>Nome:</b></td><td>{st.session_state.orcamento['nome_cliente']}</td></tr>
            <tr><td><b>WhatsApp:</b></td><td>{st.session_state.orcamento['telefone_cliente']}</td></tr>
            <tr><td><b>Peça:</b></td><td>{st.session_state.orcamento['nome_peca'] or '-'}</td></tr>
            <tr><td><b>Tempo de Impressão:</b></td><td>{st.session_state.orcamento['tempo_impressao']} horas</td></tr>
            <tr><td><b>Filamentos:</b></td><td>{filamentos_html}</td></tr>
            <tr><td><b>Valor estimado:</b></td><td style='font-size:1.3rem; color:#ff4ecd;'><b>R$ {valor_formatado}</b></td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
        st.caption("Este valor é uma estimativa. O valor final pode variar após análise do projeto.")

        # Gere o link do WhatsApp sempre que houver orçamento
        numero_whatsapp = "5541997730248"
        mensagem = f"""Olá! Gostaria de solicitar um orçamento para impressão 3D:\n\nNome: {st.session_state.orcamento['nome_cliente']}\nWhatsApp: {st.session_state.orcamento['telefone_cliente']}\nPeça: {st.session_state.orcamento['nome_peca'] or '-'}\nTempo de impressão: {st.session_state.orcamento['tempo_impressao']} horas\n"""
        for fil in st.session_state.orcamento['filamentos_utilizados']:
            mensagem += f"Filamento: {fil['descricao']} - {fil['quantidade_g_utilizada']}g\n"
        mensagem += f"Valor estimado: R$ {valor_formatado}"
        if st.session_state.orcamento['anexos']:
            mensagem += "\nAnexos: " + "; ".join(st.session_state.orcamento['anexos'])
        mensagem += "\n\nAguardo retorno!"
        mensagem_url = urllib.parse.quote(mensagem)
        st.session_state.whatsapp_link = f"https://wa.me/{numero_whatsapp}?text={mensagem_url}"

        if st.session_state.orcamento:
            if not st.session_state.orcamento_enviado:
                if st.button("Solicitar orçamento via WhatsApp", key="btn_solicitar_orcamento_whatsapp"):
                    with st.spinner("Registrando orçamento..."):
                        sucesso = False
                        erro = None
                        if IS_PUBLIC:
                            dados = [
                                st.session_state.orcamento['nome_cliente'],
                                st.session_state.orcamento['telefone_cliente'],
                                st.session_state.orcamento['nome_peca'],
                                st.session_state.orcamento['tempo_impressao'],
                                "; ".join([f"{fil['descricao']} - {fil['quantidade_g_utilizada']}g" for fil in st.session_state.orcamento['filamentos_utilizados']]),
                                f"R$ {valor_formatado}",
                                str(datetime.date.today()),
                                next((a for a in st.session_state.orcamento['anexos'] if a.startswith('Link:')), ''),
                                "", # Não há anexos de imagem/STL para links
                                next((a.replace('Link: ', '') for a in st.session_state.orcamento['anexos'] if a.startswith('Link:')), '')
                            ]
                            try:
                                enviar_pedido_google_sheets(dados)
                                sucesso = True
                            except Exception as e:
                                erro = f"Erro ao salvar no Google Sheets: {e}"
                        else:
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
                                    sucesso = True
                                except Exception as e:
                                    erro = f"Erro ao registrar orçamento: {e}"
                        if sucesso:
                            st.session_state.orcamento_enviado = True
                            st.success("Orçamento enviado com sucesso! Agora clique abaixo para enviar pelo WhatsApp.")
                        else:
                            st.error(erro)

            if st.session_state.orcamento_enviado and st.session_state.whatsapp_link:
                st.markdown(f'''
                    <a href="{st.session_state.whatsapp_link}" target="_blank" style="display:block; text-align:center; margin: 1.5rem 0;">
                        <button style="background: linear-gradient(90deg, #ff4ecd 0%, #7c3aed 100%); color: white; border: none; border-radius: 8px; padding: 1rem 2.5rem; font-size: 1.3rem; font-weight: bold; box-shadow: 0 0 16px #ff4ecd88; cursor:pointer; display: flex; align-items: center; justify-content: center; gap: 0.7rem;">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="32" style="vertical-align:middle;"> Enviar pelo WhatsApp
                        </button>
                    </a>
                ''', unsafe_allow_html=True)

    # Limpa orçamento se qualquer campo relevante mudar
    if (
        st.session_state.get('orcamento') and (
            st.session_state.orcamento.get('nome_cliente') != nome_cliente or
            st.session_state.orcamento.get('telefone_cliente') != telefone_cliente or
            st.session_state.orcamento.get('nome_peca') != nome_peca or
            st.session_state.orcamento.get('tempo_impressao') != tempo_impressao or
            st.session_state.orcamento.get('filamentos_utilizados') != st.session_state.filamentos_lista or
            st.session_state.orcamento.get('anexos') != [f"Link: {link_extra}"] # Adicionado para verificar o link
        )
    ):
        st.session_state.orcamento = None
        st.session_state.orcamento_enviado = False
