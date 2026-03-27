import streamlit as st
import pandas as pd
import os
from datetime import date

# --- CONFIGURAÇÕES DE CAMINHO ---
BASE_DIR = os.getcwd()
CSV_PATH = os.path.join(BASE_DIR, 'convidados.csv')
PASTA_UPLOADS = os.path.join(BASE_DIR, 'fotos_convidados')
FOTO_DESTAQUE = os.path.join(BASE_DIR, 'nossa_foto.jpg')
MSG_PATH = os.path.join(BASE_DIR, 'mensagem.txt')

if not os.path.exists(PASTA_UPLOADS):
    os.makedirs(PASTA_UPLOADS)

st.set_page_config(page_title="Gilmar & Adriana 2026", layout="wide", page_icon="💍")

# --- FUNÇÃO DE LEITURA (FORÇANDO ATUALIZAÇÃO) ---
def load_data_fresh():
    if not os.path.exists(CSV_PATH):
        pd.DataFrame(columns=['id', 'nome', 'familia', 'status']).to_csv(CSV_PATH, index=False)
    return pd.read_csv(CSV_PATH, dtype={'id': str})

def save_data(df_to_save):
    df_to_save.to_csv(CSV_PATH, index=False)
    st.cache_data.clear() # Limpa a memória do Streamlit

def get_wedding_msg():
    if os.path.exists(MSG_PATH):
        try:
            with open(MSG_PATH, "r", encoding="utf-8") as f: return f.read()
        except: return "Sejam bem-vindos ao nosso grande dia!"
    return "Sejam bem-vindos ao nosso grande dia!"

# --- CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
    .stApp { background-color: #fdfbf7; font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #5d4a3e !important; text-align: center; }
    .premium-card { background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #e8e2d6; margin-bottom: 20px; }
    .name-row { background: #f9f6f2; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #d4af37; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

df = load_data_fresh()
invite_id = st.query_params.get("id")

# --- 1. ÁREA DO CONVIDADO ---
if invite_id:
    invite_id = str(invite_id).strip()
    familia_df = df[df['id'] == invite_id]
    
    if not familia_df.empty:
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            if os.path.exists(FOTO_DESTAQUE): st.image(FOTO_DESTAQUE, use_container_width=True)
            st.markdown(f"<h1>Família {familia_df['familia'].iloc[0]}</h1>", unsafe_allow_html=True)
            st.markdown(f'<div class="premium-card"><div class="invite-text">{get_wedding_msg()}</div></div>', unsafe_allow_html=True)
            
            with st.form("rsvp_individual"):
                st.write("### Confirme sua presença:")
                respostas = {}
                for idx, row in familia_df.iterrows():
                    st.markdown(f'<div class="name-row">{row["nome"]}</div>', unsafe_allow_html=True)
                    respostas[idx] = st.radio(f"Status de {row['nome']}:", ["Pendente", "Confirmado", "Não poderá ir"], 
                                             index=0 if row['status'] == "Pendente" else 1 if row['status'] == "Confirmado" else 2,
                                             key=f"r_{idx}", label_visibility="collapsed")
                
                if st.form_submit_button("Enviar Resposta"):
                    for idx, status in respostas.items():
                        df.at[idx, 'status'] = status
                    save_data(df)
                    st.success("Resposta salva! ❤️"); st.balloons()
    else:
        st.error("Convite não encontrado.")

# --- 2. PAINEL ADMIN ---
st.sidebar.title("💎 Admin")
senha = st.sidebar.text_input("Senha", type="password")

if senha == "casamento2026":
    st.title("⚙️ Gestão de Convidados")
    t1, t2, t3, t4, t5 = st.tabs(["📊 Dashboard", "📤 Importar", "📝 Novo Grupo", "🖼️ Fotos", "✍️ Texto"])
    
    with t1:
        # Forçamos a leitura aqui para o Dashboard estar sempre certo
        df_dash = load_data_fresh()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Confirmados ✅", len(df_dash[df_dash['status'] == "Confirmado"]))
        c2.metric("Não Vão ❌", len(df_dash[df_dash['status'] == "Não poderá ir"]))
        c3.metric("Pendentes ⏳", len(df_dash[df_dash['status'] == "Pendente"]))
        c4.metric("Total 👥", len(df_dash))
        
        st.write("---")
        link_base = st.text_input("Link do Site:", value="https://convite-casamento-gilmar-adriana-g2ubevcjv7rhmdoxdfoc8d.streamlit.app")
        
        for fam in sorted(df_dash['familia'].unique()):
            with st.expander(f"📁 GRUPO: {str(fam).upper()}"):
                id_f = df_dash[df_dash['familia']==fam]['id'].iloc[0]
                st.code(f"{link_base}/?id={id_f}")
                
                # Listar integrantes com botão de excluir ao lado
                for idx, row in df_dash[df_dash['familia'] == fam].iterrows():
                    col_n, col_s, col_del = st.columns([3, 1, 1])
                    col_n.write(f"👤 {row['nome']}")
                    col_s.write(f"`{row['status']}`")
                    if col_del.button("🗑️", key=f"del_ind_{idx}", help="Excluir este integrante"):
                        df_dash = df_dash.drop(idx)
                        save_data(df_dash)
                        st.rerun()
                
                st.write("---")
                if st.button(f"❌ EXCLUIR FAMÍLIA {fam.upper()} INTEIRA", key=f"del_fam_{fam}"):
                    df_dash = df_dash[df_dash['familia'] != fam]
                    save_data(df_dash)
                    st.rerun()

    with t2:
        f = st.file_uploader("Subir Lista", type=['csv', 'xlsx'])
        if f and st.button("Substituir Lista Atual"):
            df_n = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
            save_data(df_n)
            st.success("Lista atualizada!"); st.rerun()

    with t3:
        st.subheader("Inserir Novo Grupo")
        with st.form("new_g"):
            c_id, c_fam = st.columns(2)
            nid = c_id.text_input("ID do Link (ex: familia-silva)")
            nfam = c_fam.text_input("Nome da Família")
            nnome = st.text_area("Nomes (separe por vírgula)")
            if st.form_submit_button("Criar Grupo"):
                lista = [n.strip() for n in nnome.split(',') if n.strip()]
                novos = [{'id': nid, 'nome': n, 'familia': nfam, 'status': 'Pendente'} for n in lista]
                df_atual = load_data_fresh()
                df_final = pd.concat([df_atual, pd.DataFrame(novos)], ignore_index=True)
                save_data(df_final)
                st.success("Criado!"); st.rerun()

    with t4:
        fotos = [f for f in os.listdir(PASTA_UPLOADS) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        cols = st.columns(4)
        for i, f in enumerate(fotos):
            cols[i%4].image(os.path.join(PASTA_UPLOADS, f))

    with t5:
        t_conv = st.text_area("Mensagem", get_wedding_msg(), height=200)
        if st.button("Salvar Mensagem"):
            with open(MSG_PATH, "w", encoding="utf-8") as file: file.write(t_conv)
            st.success("Salvo!")

else:
    if not invite_id:
        st.markdown("<h1 style='margin-top:100px;'>Gilmar & Adriana</h1>", unsafe_allow_html=True)
        st.info("Acesse pelo link pessoal enviado no WhatsApp.")
