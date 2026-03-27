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
                        index=idx_default, 
                        key=f"c_{idx}"
                    )
                
                if st.form_submit_button("Enviar Confirmação"):
                    for idx, status in respostas.items():
                        df.at[idx, 'status'] = status
                    df.to_csv(CSV_PATH, index=False)
                    st.success("Sua resposta foi salva! Obrigado. ❤️")
                    st.balloons()
    else:
        st.error("Convite não encontrado.")

# --- 2. PAINEL ADMIN (CONTROLE TOTAL) ---
st.sidebar.title("Configurações Admin")
senha = st.sidebar.text_input("Senha de Acesso", type="password")

if senha == "casamento2026":
    st.title("⚙️ Gestão de Convidados")
    
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard & Links", "📤 Importar Dados", "📝 Editar/Excluir"])

    with tab1:
        # Quando publicar no Streamlit Cloud, altere esta URL
        url_base = "https://SEU-LINK-AQUI.streamlit.app" 
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total", len(df))
        m2.metric("Confirmados", len(df[df['status'] == "Confirmado"]))
        m3.metric("Recusados", len(df[df['status'] == "Recusado"]))
        m4.metric("Pendentes", len(df[df['status'] == "Pendente"]))

        # AGRUPAMENTO POR FAMÍLIA NO DASHBOARD
        if not df.empty:
            familias = df['familia'].unique()
            for fam in familias:
                st.markdown(f'<div class="group-header">{fam.upper()}</div>', unsafe_allow_html=True)
                convidados_fam = df[df['familia'] == fam]
                
                # Cabeçalho para alinhar os itens
                h1, h2, h3 = st.columns([2, 1, 2])
                h1.caption("NOME")
                h2.caption("STATUS")
                h3.caption("LINK INDIVIDUAL")

                for idx, row in convidados_fam.iterrows():
                    c1, c2, c3 = st.columns([2, 1, 2])
                    c1.write(f"👤 {row['nome']}")
                    
                    novo_st = c2.selectbox("Status", ["Pendente", "Confirmado", "Recusado"], 
                                         index=["Pendente", "Confirmado", "Recusado"].index(row['status']),
                                         key=f"st_{idx}", label_visibility="collapsed")
                    if novo_st != row['status']:
                        df.at[idx, 'status'] = novo_st
                        df.to_csv(CSV_PATH, index=False)
                        st.rerun()
                    
                    link = f"{url_base}/?id={row['id']}"
                    c3.markdown(f'<p class="link-text">{link}</p>', unsafe_allow_html=True)
                    st.divider()
        else:
            st.info("A lista está vazia.")

    with tab2:
        st.subheader("Upload de Lista")
        f_up = st.file_uploader("Arquivo Excel ou CSV", type=['csv', 'xlsx'])
        if f_up and st.button("Substituir Tudo"):
            df_new = pd.read_csv(f_up) if f_up.name.endswith('.csv') else pd.read_excel(f_up)
            df_new.to_csv(CSV_PATH, index=False)
            st.success("Lista atualizada!")
            st.rerun()

    with tab3:
        st.subheader("Editar Cadastro")
        nome_sel = st.selectbox("Escolha o convidado:", ["Selecione..."] + df['nome'].tolist())
        if nome_sel != "Selecione...":
            idx_e = df[df['nome'] == nome_sel].index[0]
            with st.form("edit_form"):
                enome = st.text_input("Nome", value=df.at[idx_e, 'nome'])
                efam = st.text_input("Família", value=df.at[idx_e, 'familia'])
                eid = st.text_input("ID do Link", value=df.at[idx_e, 'id'])
                
                col1, col2 = st.columns(2)
                if col1.form_submit_button("Atualizar"):
                    df.at[idx_e, 'nome'], df.at[idx_e, 'familia'], df.at[idx_e, 'id'] = enome, efam, eid
                    df.to_csv(CSV_PATH, index=False)
                    st.rerun()
                if col2.form_submit_button("🗑️ Deletar"):
                    df = df.drop(idx_e)
                    df.to_csv(CSV_PATH, index=False)
                    st.rerun()
        
        st.divider()
        st.subheader("Adicionar Novo Individual")
        with st.form("add_new"):
            st.text_input("Nome", key="new_n")
            st.text_input("Família", key="new_f")
            st.text_input("ID Link", key="new_i")
            if st.form_submit_button("Adicionar"):
                if st.session_state.new_i and st.session_state.new_n:
                    novo = pd.DataFrame([[st.session_state.new_i, st.session_state.new_n, st.session_state.new_f, "Pendente"]], columns=df.columns)
                    pd.concat([df, novo]).to_csv(CSV_PATH, index=False)
                    st.rerun()
                else:
                    st.error("Preencha o nome e o ID.")

else:
    if not invite_id:
        st.title("💍 RSVP - Gilmar & Adriana")
        st.info("Acesse pelo seu link pessoal ou faça login na lateral.")