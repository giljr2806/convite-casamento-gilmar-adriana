import streamlit as st
import pandas as pd
import os
from datetime import date

# --- CONFIGURAÇÕES DE CAMINHO ---
BASE_DIR = r'C:\Users\adria\OneDrive\Documentos\Convite_Casamento'
CSV_PATH = os.path.join(BASE_DIR, 'convidados.csv')
DATA_LIMITE = date(2026, 5, 19) 

st.set_page_config(page_title="RSVP - Gilmar & Adriana", layout="wide", page_icon="💍")

# --- FUNÇÃO PARA CARREGAR DADOS ---
def load_data():
    column_names = ['id', 'nome', 'familia', 'status']
    if not os.path.exists(CSV_PATH):
        df_init = pd.DataFrame(columns=column_names)
        df_init.to_csv(CSV_PATH, index=False)
        return df_init
    try:
        df_read = pd.read_csv(CSV_PATH)
        return df_read if not df_read.empty else pd.DataFrame(columns=column_names)
    except:
        return pd.DataFrame(columns=column_names)

df = load_data()

# --- ESTILO VISUAL ---
st.markdown("""
    <style>
    .group-header { background-color: #f0f2f6; padding: 10px; border-radius: 5px; font-weight: bold; margin: 15px 0 5px 0; border-left: 5px solid #ff4b4b; }
    .link-text { font-size: 12px; color: #007bff; word-break: break-all; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
query_params = st.query_params
invite_id = query_params.get("id")

# --- 1. ÁREA DO CONVIDADO (RESTRITA A CONFIRMAR/RECUSAR) ---
if invite_id:
    familia_df = df[df['id'] == invite_id]
    if not familia_df.empty:
        st.header(f"Olá, Família {familia_df['familia'].iloc[0]}! 🥂")
        if date.today() > DATA_LIMITE:
            st.error("⚠️ O prazo para confirmação online encerrou.")
        else:
            with st.form("form_rsvp"):
                st.write("Por favor, confirme sua presença:")
                respostas = {}
                for idx, row in familia_df.iterrows():
                    current_status = row['status']
                    idx_default = 0 if current_status == "Confirmado" else 1 if current_status == "Recusado" else 0
                    
                    respostas[idx] = st.radio(
                        f"Presença de **{row['nome']}**:", 
                        ["Confirmado", "Recusado"], 
                        index=idx_default,import streamlit as st
import pandas as pd
import os
from datetime import date
from PIL import Image

# --- CONFIGURAÇÕES DE CAMINHO (DINÂMICO PARA DEPLOY) ---
# Usamos o diretório atual do sistema onde o app está rodando
BASE_DIR = os.getcwd()

CSV_PATH = os.path.join(BASE_DIR, 'convidados.csv')
PASTA_UPLOADS = os.path.join(BASE_DIR, 'fotos_convidados')
FOTO_DESTAQUE = os.path.join(BASE_DIR, 'nossa_foto.jpg')
MSG_PATH = os.path.join(BASE_DIR, 'mensagem.txt')
DATA_LIMITE = date(2026, 5, 19) 

# Garantir que a pasta de fotos exista no servidor
if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

st.set_page_config(page_title="Gilmar & Adriana 2026", layout="wide", page_icon="💍")

# --- CSS PREMIUM (LUXO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
    .stApp { background-color: #fdfbf7; font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #5d4a3e !important; text-align: center; }
    .premium-card { background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #e8e2d6; text-align: center; margin-bottom: 20px; }
    .invite-text { font-size: 1.2rem; color: #6b5b4a; font-style: italic; white-space: pre-wrap; }
    .gold-divider { height: 2px; background: linear-gradient(to right, transparent, #d4af37, transparent); margin: 20px 0; }
    .link-text { font-size: 11px; color: #8e735b; background: #f9f6f2; padding: 5px; border-radius: 5px; border: 1px solid #eee; word-break: break-all; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def load_data():
    column_names = ['id', 'nome', 'familia', 'status']
    if not os.path.exists(CSV_PATH):
        df_init = pd.DataFrame(columns=column_names)
        df_init.to_csv(CSV_PATH, index=False)
        return df_init
    try:
        return pd.read_csv(CSV_PATH)
    except:
        return pd.DataFrame(columns=column_names)

def get_wedding_msg():
    if os.path.exists(MSG_PATH):
        try:
            with open(MSG_PATH, "r", encoding="utf-8") as f: return f.read()
        except: return "Sejam bem-vindos ao nosso grande dia!"
    return "Sejam bem-vindos ao nosso grande dia!"

df = load_data()
query_params = st.query_params
invite_id = query_params.get("id")

# --- 1. ÁREA DO CONVIDADO ---
if invite_id:
    familia_df = df[df['id'] == str(invite_id)]
    if not familia_df.empty:
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            if os.path.exists(FOTO_DESTAQUE):
                st.image(FOTO_DESTAQUE, use_container_width=True)
            
            st.markdown(f"<h1>Família {familia_df['familia'].iloc[0]}</h1>", unsafe_allow_html=True)
            st.markdown(f'<div class="premium-card"><div class="invite-text">{get_wedding_msg()}</div><div class="gold-divider"></div></div>', unsafe_allow_html=True)

            if date.today() > DATA_LIMITE:
                st.error("O prazo de confirmação encerrou.")
            else:
                with st.form("rsvp_form"):
                    st.write("### Confirmar Presença")
                    respostas = {}
                    for idx, row in familia_df.iterrows():
                        respostas[idx] = st.radio(f"Presença de **{row['nome']}**:", ["Confirmado", "Recusado"], 
                                                 index=0 if row['status'] == "Confirmado" else 1 if row['status'] == "Recusado" else 0,
                                                 key=f"c_{idx}")
                    if st.form_submit_button("Enviar Resposta"):
                        for idx, status in respostas.items():
                            df.at[idx, 'status'] = status
                        df.to_csv(CSV_PATH, index=False)
                        st.success("Resposta salva! ❤️"); st.balloons()
            
            st.divider()
            st.write("### 📸 Envie uma foto para nós")
            f_up = st.file_uploader("Upload", type=["jpg", "png"], label_visibility="collapsed")
            if f_up:
                with open(os.path.join(PASTA_UPLOADS, f"{invite_id}_{f_up.name}"), "wb") as f:
                    f.write(f_up.getbuffer())
                st.toast("Foto enviada!")
    else:
        st.error("Convite não encontrado.")

# --- 2. PAINEL ADMIN ---
st.sidebar.title("💎 Admin")
senha = st.sidebar.text_input("Senha", type="password")

if senha == "casamento2026":
    st.title("⚙️ Gestão de Convidados")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📤 Importar Lista", "📝 Editar/Excluir", "🖼️ Fotos Recebidas", "✍️ Texto Convite"])

    with tab1:
        # Pega a URL atual dinamicamente
        url_base = st.get_option("browser.gatherUsageStats") # Apenas placeholder, o ideal é colar o link fixo abaixo
        # RECOMENDAÇÃO: Substitua a linha abaixo pelo seu link real do Streamlit
        url_site = "https://SEU-APP.streamlit.app"
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", len(df)); m2.metric("Confirmados", len(df[df['status'] == "Confirmado"]))
        m3.metric("Recusados", len(df[df['status'] == "Recusado"])); m4.metric("Pendentes", len(df[df['status'] == "Pendente"]))
        
        for fam in df['familia'].unique():
            with st.expander(f"FAMÍLIA {str(fam).upper()}"):
                for idx, row in df[df['familia'] == fam].iterrows():
                    c1, c2, c3 = st.columns([2,1,2])
                    c1.write(f"👤 {row['nome']}")
                    c2.write(f"`{row['status']}`")
                    link = f"{url_site}/?id={row['id']}"
                    c3.markdown(f'<div class="link-text">{link}</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("Substituir Lista Atual")
        file = st.file_uploader("Arraste seu Excel ou CSV", type=['csv', 'xlsx'])
        if file and st.button("Confirmar Importação"):
            df_new = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
            df_new.to_csv(CSV_PATH, index=False)
            st.success("Lista atualizada!"); st.rerun()

    with tab3:
        st.subheader("Editar Convidado")
        nome_sel = st.selectbox("Selecione:", ["Selecione..."] + df['nome'].tolist())
        if nome_sel != "Selecione...":
            idx_e = df[df['nome'] == nome_sel].index[0]
            with st.form("edit"):
                enome = st.text_input("Nome", df.at[idx_e, 'nome'])
                efam = st.text_input("Família", df.at[idx_e, 'familia'])
                eid = st.text_input("ID", df.at[idx_e, 'id'])
                if st.form_submit_button("Atualizar"):
                    df.at[idx_e, 'nome'], df.at[idx_e, 'familia'], df.at[idx_e, 'id'] = enome, efam, eid
                    df.to_csv(CSV_PATH, index=False); st.rerun()

    with tab4:
        st.subheader("Fotos enviadas")
        lista_fotos = os.listdir(PASTA_UPLOADS)
        if lista_fotos:
            cols = st.columns(4)
            for i, f_name in enumerate(lista_fotos):
                with cols[i % 4]:
                    st.image(os.path.join(PASTA_UPLOADS, f_name), use_container_width=True)

    with tab5:
        novo_txt = st.text_area("Texto do Convite", get_wedding_msg(), height=200)
        if st.button("Salvar Mensagem"):
            with open(MSG_PATH, "w", encoding="utf-8") as f: f.write(novo_txt)
            st.success("Texto atualizado!")

else:
    if not invite_id:
        st.markdown("<h1 style='margin-top:50px;'>Gilmar & Adriana</h1><p style='text-align:center;'>28.06.2026</p>", unsafe_allow_html=True)
        if os.path.exists(FOTO_DESTAQUE): st.image(FOTO_DESTAQUE, use_container_width=True)
        st.info("Utilize o link do seu convite para confirmar presença.")
