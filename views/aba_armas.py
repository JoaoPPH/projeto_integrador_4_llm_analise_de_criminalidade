import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests

def renderizar_aba_armas(df):
    st.header("3. Análise da Quantidade de Armas Apreendidas por Tipo")
    
    st.markdown("#### Filtros da Análise de Armas")
    col_uf_a, col_ano_a = st.columns(2)
    
    with col_uf_a:
        lista_uf_a = sorted(df['uf'].dropna().unique())
        ufs_selecionadas_a = st.multiselect("Filtrar por Estado (UF):", options=lista_uf_a, key="multiselect_uf_a")
        
    with col_ano_a:
        lista_anos_a = sorted(df[df['Ano'] < 2026]['Ano'].unique())
        anos_selecionados_a = st.multiselect("Filtrar por Ano:", options=lista_anos_a, key="multiselect_ano_a")

    df_armas_base = df[(df['Ano'] < 2026) & (df['evento'] == 'Arma de Fogo Apreendida')].copy()
    if ufs_selecionadas_a:
        df_armas_base = df_armas_base[df_armas_base['uf'].isin(ufs_selecionadas_a)]
    if anos_selecionados_a:
        df_armas_base = df_armas_base[df_armas_base['Ano'].isin(anos_selecionados_a)]

    subabas_a = st.tabs([
        "Visão Geral de Armas Apreendidas", 
        "Evolução Temporal de Apreensões", 
        "Análise Espacial por Estado"
    ])

    with subabas_a[0]:
        st.subheader("Distribuição Total de Armas de Fogo Apreendidas por Tipo")
        df_tipo_arma = df_armas_base.groupby('arma')['total'].sum().reset_index().sort_values(by='total', ascending=False)
        total_geral_armas = df_tipo_arma['total'].sum()
        df_tipo_arma['Porcentagem (%)'] = (df_tipo_arma['total'] / total_geral_armas * 100) if total_geral_armas > 0 else 0
        df_tipo_arma = df_tipo_arma.rename(columns={'total': 'Quantidade Apreendida', 'arma': 'Tipo de Arma'})
        
        fig_tipo_arma = px.bar(df_tipo_arma, x='Quantidade Apreendida', y='Tipo de Arma', orientation='h', title='Total de Apreensões por Tipo de Arma', color='Quantidade Apreendida', color_continuous_scale='Blues')
        fig_tipo_arma.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_tipo_arma, width="stretch")
        st.divider()
        st.dataframe(df_tipo_arma.style.format({'Quantidade Apreendida': '{:,.0f}', 'Porcentagem (%)': '{:.2f}%'}), width="stretch", hide_index=True)

    with subabas_a[1]:
        st.subheader("Evolução Histórica das Apreensões de Armas")
        df_temporal_arma = df_armas_base.groupby(['Ano', 'arma'])['total'].sum().reset_index()
        fig_temp_arma = px.bar(df_temporal_arma, x='Ano', y='total', color='arma', barmode='group', title='Evolução Temporal de Apreensões por Categoria')
        fig_temp_arma.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_temp_arma, width="stretch")

    with subabas_a[2]:
        st.subheader("Distribuição Geográfica das Apreensões")
        @st.cache_data
        def carregar_geojson_armas():
            return requests.get("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson").json()
        geojson_br = carregar_geojson_armas()
        
        df_mapa_armas = df_armas_base.pivot_table(index='uf', columns='arma', values='total', aggfunc='sum', fill_value=0).reset_index()
        df_mapa_armas['uf'] = df_mapa_armas['uf'].astype(str).str.upper().str.strip()
        colunas_armas = list(df_mapa_armas.columns[1:])
        df_mapa_armas['Total de Armas'] = df_mapa_armas[colunas_armas].sum(axis=1)
        
        for arma in colunas_armas:
            df_mapa_armas[f'{arma} (%)'] = np.where(df_mapa_armas['Total de Armas'] > 0, (df_mapa_armas[arma] / df_mapa_armas['Total de Armas'] * 100).round(2), 0)
            
        fig_mapa_armas = px.choropleth(df_mapa_armas, geojson=geojson_br, locations='uf', featureidkey="properties.sigla", color='Total de Armas', hover_name='uf', title='<b>Apreensão de Armas por Estado</b>', color_continuous_scale="Viridis")
        fig_mapa_armas.update_geos(fitbounds="locations", visible=False)
        fig_mapa_armas.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=600, template="plotly_white")
        st.plotly_chart(fig_mapa_armas, width="stretch")