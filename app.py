import streamlit as st
import pandas as pd
from database.models import init_db

# Importando as funções de cada aba modularizada na pasta views/
from views.aba_geral import renderizar_aba_geral
from views.aba_genero import renderizar_aba_genero
from views.aba_armas import renderizar_aba_armas
from views.aba_agentes import renderizar_aba_agentes
from views.aba_drogas import renderizar_aba_drogas

from views.aba_analise_ia import renderizar_aba_analise_ia

# Configurando a página do Streamlit
st.set_page_config(page_title="Análise de Criminalidade - PIC4", layout="wide")

# Título principal do Dashboard
st.title("Análise de Criminalidade - Projeto Integrador 4")

# Função para carregar os dados diretamente do PostgreSQL (com CACHE do Streamlit)
@st.cache_data
def carregar_dados_do_banco():
    engine = init_db()
    query = 'SELECT * FROM "ocorrencias_criminalidade"'
    df = pd.read_sql(query, con=engine)
    
    # Converte a data e extrai o Ano para manter compatibilidade com os filtros existentes
    if 'data_referencia' in df.columns:
        df['data_referencia'] = pd.to_datetime(df['data_referencia'], errors='coerce')
        df['Ano'] = df['data_referencia'].dt.year
        
    return df

with st.spinner('Carregando os dados do Banco de Dados PostgreSQL...'):
    df = carregar_dados_do_banco()

# Informações Gerais Sobre a Base de Dados
st.markdown("### Visão Geral")
col1, col2 = st.columns(2)
col1.metric("Total de Registros", f"{len(df):,}")
col2.metric("Total de Colunas", f"{df.shape[1]}")

st.divider()

# -------------------------------------------------------------
# CRIAÇÃO DAS ABAS PRINCIPAIS
# -------------------------------------------------------------
abas = st.tabs([
    "1. Análises Gerais de Crimes", 
    "2. Vitimas por Gênero", 
    "3. Armas apreendidas", 
    "4. Morte de Agente", 
    "5. Drogas Apreendidas",
    "6. Análise com IA"
])

# 1. Análise do número de crimes em cada Estado/Município
with abas[0]:
    renderizar_aba_geral(df)

# 2. Análise do número de vítimas por gênero
with abas[1]:
    renderizar_aba_genero(df)

# 3. Análise da Quantidade de Armas apreendidas por Tipo
with abas[2]:
    renderizar_aba_armas(df)

# 4. Analise de Risco de Morte por Tipo de Agente
with abas[3]:
    renderizar_aba_agentes(df)

# 5. Análise da Quantidade de Drogas apreendidas (total_peso)
with abas[4]:
    renderizar_aba_drogas(df)

# 5. Análise da Quantidade de Drogas apreendidas (total_peso)
with abas[5]:
    renderizar_aba_analise_ia(df)