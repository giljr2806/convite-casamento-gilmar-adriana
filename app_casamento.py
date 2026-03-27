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

# --- FUNÇÕES ---
def load_data():
    if not os.path.exists(CSV_PATH):
        pd.DataFrame(columns=['id', 'nome', 'familia', 'status']).to_csv(CSV_PATH, index=False)
    # Lemos direto do arquivo para garantir que exclusões apareçam na hora
    return pd.read_csv(CSV_PATH, dtype={'id': str})

def get_wedding_msg():
    if os.path.exists(MSG_PATH):
        try:
            with open(MSG_PATH, "r", encoding="utf-8") as f: return f.read()
        except: return "Sejam bem-vindos ao nosso grande dia!"
    return "Sejam bem-vindos ao nosso grande dia!"

# Carregamos os dados no início
df = load_data()
invite_id = st.query_params.get("id")

# --- CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
    .stApp { background-color: #fdfbf7; font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #5d4a3e !important; text-align: center; }
    .premium-card { background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #e8e2d6; margin-bottom: 20px; }
    .invite-text { font-size: 1.2rem; color: #6b5b4a; font-style: italic; text-align: center; white-space: pre-wrap; }
    .name-row { background: #f9f6f2; padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. ÁREA DO CONVIDADO ---
if invite_id:
    invite_id = str(invite_id).strip()
    familia_df = df[df['id'] == invite_id]
    
    if not familia_df.empty:
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            if os.path.exists(FOTO_DESTAQUE): 
                st.image(FOTO_DESTAQUE, use_container_width=True)
            
            st.markdown(f"<h1>Família {familia_df['familia'].iloc[0]}</h1>", unsafe_allow_html=True)
            st.markdown(f'<div class="premium-card"><div class="invite-text">{get_wedding_msg()}</div></div>', unsafe_allow_html=True)
            
            st.markdown("### Confirme sua presença:")
            with st.form("rsvp_individual"):
                respostas = {}
                for idx, row in familia_df.iterrows():
                    st.markdown(f'<div class="name-row"><b>{row["nome"]}</b></div>', unsafe_allow_html=True)
                    respostas[idx] = st.radio(
                        f"Presença de {row['nome']}:",
                        ["Pendente", "Confirmado", "Não poderá ir"],
                        index=0 if row['status'] == "Pendente" else 1 if row['status'] == "Confirmado" else 2,
                        key=f"rsvp_{idx}",
                        label_visibility="collapsed"
                    )
                
                if st.form_submit_button("Enviar Confirmação"):
                    # Atualizamos o DF original e salvamos
                    for idx, status_novo in respostas.items():
                        df.at[idx, 'status'] = status_novo
                    df.to_csv(CSV_PATH, index=False)
                    st.success("Resposta salva! ❤️")
                    st.balloons()
            st.divider()
    else:
        st.error("Convite não encontrado.")

# --- 2. PAINEL ADMIN ---
st.sidebar.title("💎 Painel Admin")
senha = st.sidebar.text_input("Senha", type="password")

if senha == "casamento2026":
    st.title("⚙️ Gestão")
    t1, t2, t3, t4, t5 = st.tabs(["📊 Dashboard", "📤 Importar", "📝 Editar/Inserir", "🖼️ Fotos", "✍️ Texto"])
    
    with t1:
        # Link base dinâmico (pegando o seu link atual da imagem)
        link_base_site = st.text_input("Link Base:", value="https://convite-casamento-gilmar-adriana-g2ubevcjv7rhmdoxdfoc8d.streamlit.app")
        
        # Recalcular métricas SEMPRE que a página carregar
        m_conf = len(df[df['status'] == "Confirmado"])
        m_nao = len(df[df['status'] == "Não poderá ir"])
        m_pend = len(df[df['status'] == "Pendente"])
        m_total = len(df)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Confirmados", m_conf)
        c2.metric("Não Vão", m_nao)
        c3.metric("Pendentes", m_pend)
        c4.metric("Total", m_total)
        
        for fam in df['familia'].unique():
            with st.expander(f"GRUPO: {str(fam).upper()}"):
                id_f = df[df['familia']==fam]['id'].iloc[0]
                st.code(f"{link_base_site}/?id={id_f}")
                st.table(df[df['familia'] == fam][['nome', 'status']])

    with t2:
        f = st.file_uploader("Subir Lista", type=['csv', 'xlsx'])
        if f and st.button("Substituir Lista"):
            df_n = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
            df_n.to_csv(CSV_PATH, index=False)
            st.success("Importado!"); st.rerun()

    with t3:
        st.subheader("Adicionar Novo Grupo")
        with st.form("add_manual"):
            new_id = st.text_input("ID do Link (ex: familia-silva)")
            new_fam = st.text_input("Sobrenome")
            new_names = st.text_area("Nomes (separados por vírgula)")
            if st.form_submit_button("Criar Grupo"):
                lista_nomes = [n.strip() for n in new_names.split(',') if n.strip()]
                novos = [{'id': new_id, 'nome': n, 'familia': new_fam, 'status': 'Pendente'} for n in lista_nomes]
                df_final = pd.concat([df, pd.DataFrame(novos)], ignore_index=True)
                df_final.to_csv(CSV_PATH, index=False); st.rerun()
        
        st.divider()
        st.subheader("Gerenciar Cadastrados")
        if not df.empty:
            fam_to_edit = st.selectbox("Escolha o grupo:", sorted(df['familia'].unique()))
            
            if st.button(f"🗑️ EXCLUIR GRUPO '{fam_to_edit}' INTEIRO"):
                df_restante = df[df['familia'] != fam_to_edit]
                df_restante.to_csv(CSV_PATH, index=False)
                st.success("Excluído!"); st.rerun()

            for idx, row in df[df['familia'] == fam_to_edit].iterrows():
                col1, col2, col3 = st.columns([3, 1, 1])
                new_n = col1.text_input("Nome", value=row['nome'], key=f"e_{idx}")
                if col2.button("💾", key=f"s_{idx}"):
                    df.at[idx, 'nome'] = new_n
                    df.to_csv(CSV_PATH, index=False); st.success("Salvo!")
                if col3.button("🗑️", key=f"d_{idx}"):
                    df = df.drop(idx)
                    df.to_csv(CSV_PATH, index=False); st.rerun()

    with t4:
        fotos = os.listdir(PASTA_UPLOADS)
        cols = st.columns(4)
        for i, f_n in enumerate(fotos):
            cols[i%4].image(os.path.join(PASTA_UPLOADS, f_n))

    with t5:
        msg = st.text_area("Mensagem do Convite", get_wedding_msg(), height=200)
        if st.button("Salvar Mensagem"):
            with open(MSG_PATH, "w", encoding="utf-8") as f: f.write(msg)
            st.success("Salvo!")

else:
    if not invite_id:
        st.markdown("<h1 style='margin-top:80px;'>Gilmar & Adriana</h1>", unsafe_allow_html=True)
        st.info("Acesse pelo link enviado no seu WhatsApp.")
