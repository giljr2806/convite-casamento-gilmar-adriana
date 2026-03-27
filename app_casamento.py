import streamlit as st
import pandas as pd
import os
from datetime import date
from PIL import Image

# --- CONFIGURAÇÕES DE CAMINHO ---
BASE_DIR = os.getcwd()
CSV_PATH = os.path.join(BASE_DIR, 'convidados.csv')
PASTA_UPLOADS = os.path.join(BASE_DIR, 'fotos_convidados')
FOTO_DESTAQUE = os.path.join(BASE_DIR, 'nossa_foto.jpg')
MSG_PATH = os.path.join(BASE_DIR, 'mensagem.txt')
DATA_LIMITE = date(2026, 5, 19) 

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

st.set_page_config(page_title="Gilmar & Adriana 2026", layout="wide", page_icon="💍")

# --- CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
    .stApp { background-color: #fdfbf7; font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #5d4a3e !important; text-align: center; }
    .premium-card { background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #e8e2d6; text-align: center; margin-bottom: 20px; }
    .invite-text { font-size: 1.2rem; color: #6b5b4a; font-style: italic; white-space: pre-wrap; }
    .gold-divider { height: 2px; background: linear-gradient(to right, transparent, #d4af37, transparent); margin: 20px 0; }
    .link-text { font-size: 11px; color: #8e735b; background: #f9f6f2; padding: 5px; border-radius: 5px; border: 1px solid #eee; word-break: break-all; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def load_data():
    if not os.path.exists(CSV_PATH):
        pd.DataFrame(columns=['id', 'nome', 'familia', 'status']).to_csv(CSV_PATH, index=False)
    return pd.read_csv(CSV_PATH, dtype={'id': str})

def get_wedding_msg():
    if os.path.exists(MSG_PATH):
        with open(MSG_PATH, "r", encoding="utf-8") as f: return f.read()
    return "Sejam bem-vindos ao nosso grande dia!"

df = load_data()
invite_id = st.query_params.get("id")

# --- 1. ÁREA DO CONVIDADO ---
if invite_id:
    familia_df = df[df['id'] == str(invite_id)]
    if not familia_df.empty:
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            if os.path.exists(FOTO_DESTAQUE): st.image(FOTO_DESTAQUE, use_container_width=True)
            st.markdown(f"<h1>Família {familia_df['familia'].iloc[0]}</h1>", unsafe_allow_html=True)
            st.markdown(f'<div class="premium-card"><div class="invite-text">{get_wedding_msg()}</div><div class="gold-divider"></div></div>', unsafe_allow_html=True)
            
            with st.form("rsvp"):
                st.write("### Confirmar Presença")
                respostas = {}
                for idx, row in familia_df.iterrows():
                    respostas[idx] = st.radio(f"Status de **{row['nome']}**:", ["Confirmado", "Recusado"], index=0 if row['status']=="Confirmado" else 1 if row['status']=="Recusado" else 0, key=f"c_{idx}")
                if st.form_submit_button("Confirmar"):
                    for idx, stt in respostas.items(): df.at[idx, 'status'] = stt
                    df.to_csv(CSV_PATH, index=False)
                    st.success("Salvo! ❤️"); st.balloons()
            
            st.divider()
            f_up = st.file_uploader("📸 Envie uma foto", type=["jpg", "png", "jpeg"])
            if f_up:
                with open(os.path.join(PASTA_UPLOADS, f"{invite_id}_{f_up.name}"), "wb") as f: f.write(f_up.getbuffer())
                st.toast("Foto enviada!")
    else:
        st.error("Convite não encontrado.")

# --- 2. PAINEL ADMIN ---
st.sidebar.title("💎 Admin")
senha = st.sidebar.text_input("Senha", type="password")

if senha == "casamento2026":
    st.title("⚙️ Gestão")
    t1, t2, t3, t4, t5 = st.tabs(["📊 Dashboard", "📤 Importar", "📝 Editar/Novo", "🖼️ Fotos", "✍️ Texto"])
    
    with t1:
        # Tenta pegar o link do próprio navegador, se falhar, usa o que você digitar
        current_url = st.text_input("Confirme o Link Base do Site (ex: https://meu-app.streamlit.app)", value="https://giljr2806-convite-casamento-gilmar-adriana-app-casamento-3qg69s.streamlit.app")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Confirmados", len(df[df['status'] == "Confirmado"]))
        m2.metric("Pendentes", len(df[df['status'] == "Pendente"]))
        m3.metric("Total", len(df))
        
        for fam in df['familia'].unique():
            with st.expander(f"FAMÍLIA {str(fam).upper()}"):
                link_fam = f"{current_url}/?id={df[df['familia']==fam]['id'].iloc[0]}"
                st.markdown(f"🔗 **Link do Grupo:** `{link_fam}`")
                st.write("---")
                for _, row in df[df['familia'] == fam].iterrows():
                    st.write(f"👤 {row['nome']} - `{row['status']}`")

    with t2: # Importar
        f = st.file_uploader("Arquivo Excel/CSV", type=['csv', 'xlsx'])
        if f and st.button("Confirmar Importação"):
            df_n = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
            df_n.to_csv(CSV_PATH, index=False); st.rerun()

    with t3: # Novo Grupo
        with st.form("novo"):
            id_n = st.text_input("ID do Link (ex: familia-silva)")
            fam_n = st.text_input("Nome da Família")
            nomes_n = st.text_area("Integrantes (separe por vírgula)")
            if st.form_submit_button("Salvar Grupo"):
                lista = [n.strip() for n in nomes_n.split(',') if n.strip()]
                novos = [{'id': id_n, 'nome': n, 'familia': fam_n, 'status': 'Pendente'} for n in lista]
                pd.concat([df, pd.DataFrame(novos)]).to_csv(CSV_PATH, index=False); st.rerun()

    with t4: # Fotos
        fotos = os.listdir(PASTA_UPLOADS)
        cols = st.columns(4)
        for i, f_n in enumerate(fotos):
            cols[i%4].image(os.path.join(PASTA_UPLOADS, f_n))

    with t5: # Texto
        txt_at = get_wedding_msg()
        novo_txt = st.text_area("Texto do Convite", value=txt_at, height=200)
        if st.button("Salvar Mensagem"):
            with open(MSG_PATH, "w", encoding="utf-8") as f_m: f_m.write(novo_txt)
            st.success("Texto atualizado!")

else:
    if not invite_id:
        st.markdown("<h1 style='margin-top:50px;'>Gilmar & Adriana</h1>", unsafe_allow_html=True)
        if os.path.exists(FOTO_DESTAQUE): st.image(FOTO_DESTAQUE, use_container_width=True)
        st.info("Acesse pelo seu link pessoal.")
