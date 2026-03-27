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

# --- CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400&display=swap');
    .stApp { background-color: #fdfbf7; font-family: 'Lato', sans-serif; }
    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #5d4a3e !important; text-align: center; }
    .premium-card { background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #e8e2d6; text-align: center; margin-bottom: 20px; }
    .invite-text { font-size: 1.2rem; color: #6b5b4a; font-style: italic; white-space: pre-wrap; }
    .link-text { font-size: 11px; color: #8e735b; background: #f9f6f2; padding: 5px; border-radius: 5px; border: 1px solid #eee; word-break: break-all; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. ÁREA DO CONVIDADO ---
if invite_id:
    # Remove qualquer espaço extra do ID
    invite_id = str(invite_id).strip()
    familia_df = df[df['id'] == invite_id]
    
    if not familia_df.empty:
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            if os.path.exists(FOTO_DESTAQUE): 
                st.image(FOTO_DESTAQUE, use_container_width=True)
            
            st.markdown(f"<h1>Família {familia_df['familia'].iloc[0]}</h1>", unsafe_allow_html=True)
            st.markdown(f'<div class="premium-card"><div class="invite-text">{get_wedding_msg()}</div></div>', unsafe_allow_html=True)
            
            with st.form("rsvp"):
                st.write("### Confirmar Presença")
                respostas = {}
                for idx, row in familia_df.iterrows():
                    respostas[idx] = st.radio(f"Status de **{row['nome']}**:", ["Confirmado", "Recusado"], 
                                             index=0 if row['status']=="Confirmado" else 1 if row['status']=="Recusado" else 0, 
                                             key=f"c_{idx}")
                
                if st.form_submit_button("Confirmar Presença"):
                    for idx, stt in respostas.items(): 
                        df.at[idx, 'status'] = stt
                    df.to_csv(CSV_PATH, index=False)
                    st.success("Resposta salva com sucesso! ❤️")
                    st.balloons()
            
            st.divider()
            f_up = st.file_uploader("📸 Compartilhe uma foto conosco", type=["jpg", "png", "jpeg"])
            if f_up:
                with open(os.path.join(PASTA_UPLOADS, f"{invite_id}_{f_up.name}"), "wb") as f:
                    f.write(f_up.getbuffer())
                st.toast("Foto enviada!")
    else:
        st.error("Convite não encontrado. Por favor, verifique o link enviado.")

# --- 2. PAINEL ADMIN ---
st.sidebar.title("💎 Admin")
senha = st.sidebar.text_input("Senha", type="password")

if senha == "casamento2026":
    st.title("⚙️ Gestão de Convidados")
    t1, t2, t3, t4, t5 = st.tabs(["📊 Dashboard", "📤 Importar", "📝 Novo Grupo", "🖼️ Fotos", "✍️ Texto"])
    
    with t1:
        # LÓGICA INTELIGENTE: Pega a URL do navegador automaticamente
        # Se não conseguir (rodando local), usa uma string vazia
        try:
            # Captura a URL base ignorando os parâmetros após a interrogação
            base_url = st.query_params.get("dummy_val", "https://") 
            # Como o Streamlit esconde a URL real, o melhor é detectar via JS ou usar o link fixo
            # Deixei um campo editável aqui para você confirmar o link base se precisar:
            link_base_site = st.text_input("Link Base do Site:", value="https://convite-casamento-gilmar-adriana-g2ubevcjv7rhmdoxdfoc8d.streamlit.app")
        except:
            link_base_site = ""

        m1, m2, m3 = st.columns(3)
        m1.metric("Confirmados", len(df[df['status'] == "Confirmado"]))
        m2.metric("Pendentes", len(df[df['status'] == "Pendente"]))
        m3.metric("Total", len(df))
        
        if not df.empty:
            for fam in df['familia'].unique():
                with st.expander(f"FAMÍLIA {str(fam).upper()}"):
                    # Pega o ID daquela família
                    id_da_fam = df[df['familia']==fam]['id'].iloc[0]
                    # Gera o link final
                    link_final = f"{link_base_site}/?id={id_da_fam}"
                    
                    st.markdown(f"🔗 **Link para WhatsApp:**")
                    st.code(link_final)
                    st.write("---")
                    st.write(df[df['familia']==fam][['nome', 'status']])
        else:
            st.info("Nenhum convidado cadastrado.")

    with t2:
        f = st.file_uploader("Subir Planilha (Excel ou CSV)", type=['csv', 'xlsx'])
        if f and st.button("Salvar Lista Completa"):
            df_n = pd.read_csv(f) if f.name.endswith('.csv') else pd.read_excel(f)
            df_n.to_csv(CSV_PATH, index=False)
            st.success("Lista salva!"); st.rerun()

    with t3:
        st.subheader("Adicionar manualmente")
        with st.form("novo"):
            id_n = st.text_input("ID do Link (ex: familia-silva)", help="Sem espaços")
            fam_n = st.text_input("Nome da Família")
            nomes_n = st.text_area("Integrantes (separe por vírgula)")
            if st.form_submit_button("Salvar Novo Grupo"):
                if id_n and nomes_n:
                    lista = [n.strip() for n in nomes_n.split(',') if n.strip()]
                    novos = [{'id': id_n, 'nome': n, 'familia': fam_n, 'status': 'Pendente'} for n in lista]
                    pd.concat([df, pd.DataFrame(novos)]).to_csv(CSV_PATH, index=False)
                    st.success("Grupo adicionado!")
                    st.rerun()

    with t4:
        fotos = os.listdir(PASTA_UPLOADS)
        if fotos:
            cols = st.columns(4)
            for i, f_n in enumerate(fotos):
                cols[i%4].image(os.path.join(PASTA_UPLOADS, f_n))
        else:
            st.info("Nenhuma foto ainda.")

    with t5:
        novo_txt = st.text_area("Texto do Convite", get_wedding_msg(), height=250)
        if st.button("Atualizar Texto"):
            with open(MSG_PATH, "w", encoding="utf-8") as f_m: f_m.write(novo_txt)
            st.success("Texto atualizado!")

else:
    if not invite_id:
        st.markdown("<h1 style='margin-top:100px;'>Gilmar & Adriana</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center; color:#d4af37;'>28 de Junho de 2026</h3>", unsafe_allow_html=True)
        if os.path.exists(FOTO_DESTAQUE): 
            st.image(FOTO_DESTAQUE, use_container_width=True)
        st.info("Por favor, acesse o site através do link pessoal enviado para sua família.")
