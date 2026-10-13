import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from sklearn.linear_model import LinearRegression

def renderizar_aba_drogas(df):
    st.header("5. Análise da Quantidade de Drogas apreendidas (total_peso)")

    # Preparação da base de drogas
    df_drogas_base = df[df['evento'].str.contains('coca|macon', case=False, na=False)].copy()
    df_drogas_base['uf'] = df_drogas_base['uf'].astype(str).str.upper().str.strip()
    
    # -------------------------------------------------------------
    # FILTROS DA ABA DE DROGAS
    # -------------------------------------------------------------
    st.markdown("#### Filtros da Análise de Drogas")
    col_drug, col_yr, col_state = st.columns(3)
    
    with col_drug:
        opcoes_droga = ["Ambos", "Cocaína", "Maconha"]
        droga_selecionada = st.radio("Tipo de Droga / Evento:", opcoes_droga, index=0, key="radio_drug_d")
        
    with col_yr:
        anos_disponiveis = sorted(df_drogas_base['Ano'].unique())
        anos_selecionados_d = st.multiselect("Selecionar Anos:", anos_disponiveis, default=anos_disponiveis, key="ms_anos_d")
        
    with col_state:
        estados_disponiveis = sorted(df_drogas_base['uf'].dropna().unique())
        estados_selecionados_d = st.multiselect("Selecionar Estados (UF):", estados_disponiveis, key="ms_estados_d")

    # Verificação e Aplicação de Filtros
    if not anos_selecionados_d:
        st.warning("⚠️ Selecione pelo menos um ano na caixa de filtros.")
    else:
        df_filtrado_d = df_drogas_base[df_drogas_base['Ano'].isin(anos_selecionados_d)].copy()
        
        if droga_selecionada != "Ambos":
            termo_busca = "coca" if droga_selecionada == "Cocaína" else "macon"
            df_filtrado_d = df_filtrado_d[df_filtrado_d['evento'].str.contains(termo_busca, case=False, na=False)]
            
        if estados_selecionados_d:
            df_filtrado_d = df_filtrado_d[df_filtrado_d['uf'].isin(estados_selecionados_d)]
            
        if df_filtrado_d.empty:
            st.warning("Nenhum registro encontrado para os filtros selecionados.")
        else:
            subabas_d = st.tabs([
                "Visão Geral",
                "Evolução Temporal", 
                "Análise Geográfica", 
                "Previsões e Tendências"
            ])
            
            # Sub-aba 1: Visão Geral
            with subabas_d[0]:
                st.subheader("Métricas Gerais de Apreensões")
                
                total_kg = df_filtrado_d['total_peso'].sum()
                total_ton = total_kg / 1000
                
                anos_ativos = [y for y in df_filtrado_d['Ano'].unique() if y != 2026]
                qtd_anos = len(anos_ativos) if len(anos_ativos) > 0 else df_filtrado_d['Ano'].nunique()
                avg_kg = df_filtrado_d[df_filtrado_d['Ano'] != 2026]['total_peso'].sum() / qtd_anos if qtd_anos > 0 else 0
                avg_ton = avg_kg / 1000
                
                totais_anuais = df_filtrado_d.groupby('Ano')['total_peso'].sum()
                ano_recorde = totais_anuais.idxmax() if not totais_anuais.empty else "N/A"
                max_ano_val = totais_anuais.max() / 1000 if not totais_anuais.empty else 0
                
                c_k1, c_k2, c_k3, c_k4 = st.columns(4)
                c_k1.metric("Peso Total Apreendido", f"{total_ton:,.2f} t", f"{total_kg:,.1f} kg")
                c_k2.metric("Média Anual (exceto 2026)", f"{avg_ton:,.2f} t/ano")
                c_k3.metric("Ano Recorde", f"{ano_recorde}", f"{max_ano_val:,.2f} t")
                c_k4.metric("Número de Ocorrências", f"{len(df_filtrado_d):,}")
            
            # Sub-aba 2: Evolução Temporal
            with subabas_d[1]:
                st.subheader("Evolução Temporal de Apreensões por Ano")
                
                drogas_tipo_ano = df_filtrado_d.groupby(['Ano', 'evento'])['total_peso'].sum().reset_index()
                drogas_tipo_ano['total_peso_t'] = drogas_tipo_ano['total_peso'] / 1000
                drogas_tipo_ano['Droga'] = drogas_tipo_ano['evento'].apply(lambda x: "Cocaína" if "coca" in str(x).lower() else "Maconha")
                
                fig_bar_d = px.bar(
                    drogas_tipo_ano, x='Ano', y='total_peso_t', color='Droga', barmode='group',
                    title='Apreensões de Drogas por Ano e Substância (Toneladas)',
                    template="plotly_white"
                )
                fig_bar_d.update_layout(xaxis=dict(tickmode='linear'))
                st.plotly_chart(fig_bar_d, width="stretch")
                
                st.markdown("#### Detalhes Consolidados por Ano (Toneladas)")
                pivot_drogas = drogas_tipo_ano.pivot_table(index='Ano', columns='Droga', values='total_peso_t', aggfunc='sum', fill_value=0)
                pivot_drogas['Total'] = pivot_drogas.sum(axis=1)
                st.dataframe(pivot_drogas.style.format("{:,.2f} t"), width="stretch")

            # Sub-aba 3: Análise Geográfica
            with subabas_d[2]:
                st.subheader("Distribuição Geográfica das Apreensões")
                
                @st.cache_data
                def carregar_geojson_drogas():
                    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
                    return requests.get(url).json()
                    
                with st.spinner('Carregando mapa interativo...'):
                    geojson_d = carregar_geojson_drogas()
                
                df_mapa_d = df_filtrado_d.groupby('uf')['total_peso'].sum().reset_index()
                df_mapa_d['total_peso_t'] = df_mapa_d['total_peso'] / 1000
                
                fig_mapa_d = px.choropleth(
                    df_mapa_d, geojson=geojson_d, locations='uf', featureidkey="properties.sigla",
                    color='total_peso_t', hover_name='uf',
                    title='Distribuição de Apreensões de Drogas (Toneladas)',
                    color_continuous_scale="Reds",
                    template="plotly_white"
                )
                fig_mapa_d.update_geos(fitbounds="locations", visible=False)
                fig_mapa_d.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=600)
                st.plotly_chart(fig_mapa_d, width="stretch")

            # Sub-aba 4: Previsões e Tendências
            with subabas_d[3]:
                st.subheader("Modelagem Preditiva e Ajuste de Curvas")
                incluir_2026 = st.checkbox("Incluir 2026 no treinamento (dados parciais)", value=False, key="chk_2026_drogas")
                
                drogas_reg = df_filtrado_d.groupby('Ano')['total_peso'].sum().reset_index()
                drogas_reg['total_peso_t'] = drogas_reg['total_peso'] / 1000
                
                treino_df = drogas_reg if incluir_2026 else drogas_reg[drogas_reg['Ano'] < 2026]
                    
                if len(treino_df) < 2:
                    st.warning("⚠️ Dados insuficientes para realizar a regressão linear.")
                else:
                    X_d = treino_df[['Ano']]
                    y_d = treino_df['total_peso_t']
                    
                    modelo_d = LinearRegression()
                    modelo_d.fit(X_d, y_d)
                    
                    anos_futuros_d = pd.DataFrame({'Ano': [2026, 2027, 2028, 2029, 2030]})
                    preds_futuras_d = modelo_d.predict(anos_futuros_d)
                    
                    fig_proj_d = go.Figure()
                    fig_proj_d.add_trace(go.Scatter(x=treino_df['Ano'], y=y_d, mode='lines+markers', name='Histórico Real'))
                    fig_proj_d.add_trace(go.Scatter(x=anos_futuros_d['Ano'], y=preds_futuras_d, mode='lines+markers', name='Previsão (2026-2030)', line=dict(dash='dot')))
                    
                    fig_proj_d.update_layout(title='Projeções de Apreensões de Drogas', template="plotly_white")
                    st.plotly_chart(fig_proj_d, width="stretch")
                    
                    st.markdown("#### Tabela de Valores Projetados")
                    df_proj_d = pd.DataFrame({'Ano': anos_futuros_d['Ano'], 'Previsão (Toneladas)': preds_futuras_d})
                    st.dataframe(df_proj_d.style.format({'Previsão (Toneladas)': '{:,.2f} t'}), hide_index=True)