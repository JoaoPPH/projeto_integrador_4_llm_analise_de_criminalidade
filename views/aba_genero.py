import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

def renderizar_aba_genero(df):
    st.header("2. Análise do Número de Vítimas por Gênero")
    
    st.markdown("#### Filtros da Análise de Gênero")
    col_uf_g, col_ano_g = st.columns(2)
    
    with col_uf_g:
        lista_uf_g = sorted(df['uf'].dropna().unique())
        ufs_selecionadas_g = st.multiselect("Filtrar por Estado (UF):", options=lista_uf_g, key="multiselect_uf_g")
        
    with col_ano_g:
        lista_anos_g = sorted(df[df['Ano'] < 2026]['Ano'].unique())
        anos_selecionados_g = st.multiselect("Filtrar por Ano:", options=lista_anos_g, key="multiselect_ano_g")

    df_filtrado_g = df[df['Ano'] < 2026].copy()
    if ufs_selecionadas_g:
        df_filtrado_g = df_filtrado_g[df_filtrado_g['uf'].isin(ufs_selecionadas_g)]
    if anos_selecionados_g:
        df_filtrado_g = df_filtrado_g[df_filtrado_g['Ano'].isin(anos_selecionados_g)]

    subabas_g = st.tabs([
        "Distribuição Total de Vítimas por Gênero", 
        "Análise Histórica de Vítimas", 
        "Distribuição de Vítimas por Gênero e Estado", 
        "Análise de Regressão", 
        "Comparação de Modelos: Regressão Linear vs Random Forest vs XGBoost"
    ])

    with subabas_g[0]:
        st.subheader("Distribuição Total de Vítimas por Gênero")
        total_masc = df_filtrado_g['masculino'].sum()
        total_fem = df_filtrado_g['feminino'].sum()
        total_ni = df_filtrado_g['nao_informado'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Vítimas Masculinas", f"{int(total_masc):,}")
        m2.metric("Vítimas Femininas", f"{int(total_fem):,}")
        m3.metric("Não Informado", f"{int(total_ni):,}")
        
        dados_pizza = pd.DataFrame({
            'Gênero': ['Masculino', 'Feminino', 'Não Informado'],
            'Total': [total_masc, total_fem, total_ni]
        })
        mapa_cores = {'Masculino': '#1f77b4', 'Feminino': '#e377c2', 'Não Informado': '#949494'}
        fig_pizza = px.pie(data_frame=dados_pizza, values='Total', names='Gênero', title='Proporção Total de Vítimas por Gênero', color='Gênero', color_discrete_map=mapa_cores)
        st.plotly_chart(fig_pizza, use_container_width=True)
        st.divider()
        
        st.markdown("#### Total de Vítimas por Tipo de Evento")
        resultados_vitimas = df_filtrado_g.groupby("evento")[["feminino", "masculino", "nao_informado"]].sum()
        resultados_vitimas['Total Geral'] = resultados_vitimas.sum(axis=1)
        resultados_vitimas = resultados_vitimas.sort_values(by='Total Geral', ascending=False)
        st.dataframe(resultados_vitimas.style.format({'feminino': '{:,.0f}', 'masculino': '{:,.0f}', 'nao_informado': '{:,.0f}', 'Total Geral': '{:,.0f}'}))

    with subabas_g[1]:
        st.subheader("Análise Histórica de Vítimas")
        df_historico_g = df_filtrado_g.groupby('Ano')[['masculino', 'feminino', 'nao_informado']].sum().reset_index()
        df_historico_g['Total Geral'] = df_historico_g['masculino'] + df_historico_g['feminino'] + df_historico_g['nao_informado']
        df_historico_g['% Masculino'] = np.where(df_historico_g['Total Geral'] > 0, (df_historico_g['masculino'] / df_historico_g['Total Geral']) * 100, 0)
        df_historico_g['% Feminino'] = np.where(df_historico_g['Total Geral'] > 0, (df_historico_g['feminino'] / df_historico_g['Total Geral']) * 100, 0)
        df_historico_g['% Não Informado'] = np.where(df_historico_g['Total Geral'] > 0, (df_historico_g['nao_informado'] / df_historico_g['Total Geral']) * 100, 0)

        df_melt = df_historico_g.melt(
            id_vars=['Ano', 'Total Geral', '% Masculino', '% Feminino', '% Não Informado'],
            value_vars=['masculino', 'feminino', 'nao_informado', 'Total Geral'],
            var_name='Gênero', value_name='Quantidade'
        )
        nomes_legenda = {'masculino': 'Masculino', 'feminino': 'Feminino', 'nao_informado': 'Não Informado', 'Total Geral': 'Total Geral'}
        df_melt['Gênero'] = df_melt['Gênero'].map(nomes_legenda)

        condicoes = [df_melt['Gênero'] == 'Masculino', df_melt['Gênero'] == 'Feminino', df_melt['Gênero'] == 'Não Informado']
        escolhas = [df_melt['% Masculino'].map('{:.1f}%'.format), df_melt['% Feminino'].map('{:.1f}%'.format), df_melt['% Não Informado'].map('{:.1f}%'.format)]
        df_melt['Porcentagem_Texto'] = np.select(condicoes, escolhas, default='')

        mapa_cores_historico = {'Masculino': '#1f77b4', 'Feminino': '#e377c2', 'Não Informado': '#949494', 'Total Geral': '#000000'}
        fig_linha_g = px.line(
            data_frame=df_melt, x='Ano', y='Quantidade', color='Gênero', color_discrete_map=mapa_cores_historico,
            title='Evolução Temporal e Proporção de Vítimas por Gênero', markers=True, text='Porcentagem_Texto', custom_data=['Total Geral']
        )
        fig_linha_g.update_traces(textposition="top center", hovertemplate="<br>".join(["<b>Ano:</b> %{x}", "<b>Quantidade:</b> %{y:,.0f}", "<b>Total Geral:</b> %{customdata[0]:,.0f}"]))
        st.plotly_chart(fig_linha_g, use_container_width=True)
        st.divider()
        st.dataframe(df_historico_g.style.format({'masculino': '{:,.0f}', '% Masculino': '{:.2f}%', 'feminino': '{:,.0f}', '% Feminino': '{:.2f}%', 'nao_informado': '{:,.0f}', '% Não Informado': '{:.2f}%', 'Total Geral': '{:,.0f}'}), hide_index=True)

    with subabas_g[2]:
        st.subheader("Distribuição de Vítimas por Gênero e Estado")
        @st.cache_data
        def carregar_geojson():
            return requests.get("https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson").json()
        geojson_br = carregar_geojson()
        
        df_mapa = df_filtrado_g.groupby('uf').agg({'feminino': 'sum', 'masculino': 'sum'}).reset_index()
        df_mapa['uf'] = df_mapa['uf'].astype(str).str.upper().str.strip()
        df_mapa['total_vitimas'] = df_mapa['feminino'] + df_mapa['masculino']
        df_mapa['perc_feminino'] = np.where(df_mapa['total_vitimas'] > 0, (df_mapa['feminino'] / df_mapa['total_vitimas'] * 100).round(2), 0)
        df_mapa['perc_masculino'] = np.where(df_mapa['total_vitimas'] > 0, (df_mapa['masculino'] / df_mapa['total_vitimas'] * 100).round(2), 0)
        
        fig_mapa_br = px.choropleth(
            data_frame=df_mapa, geojson=geojson_br, locations='uf', featureidkey="properties.sigla", color='total_vitimas', hover_name='uf',
            hover_data={'uf': False, 'total_vitimas': ':,', 'feminino': ':,', 'masculino': ':,', 'perc_feminino': ':.2f', 'perc_masculino': ':.2f'},
            title='<b>Distribuição de Vítimas por Gênero e Estado</b>', color_continuous_scale="Reds"
        )
        fig_mapa_br.update_geos(fitbounds="locations", visible=False)
        fig_mapa_br.update_layout(margin={"r":0,"t":50,"l":0,"b":0}, height=600, template="plotly_white")
        st.plotly_chart(fig_mapa_br, use_container_width=True)
        st.divider()
        st.dataframe(df_mapa.sort_values(by='total_vitimas', ascending=False).style.format({'feminino': '{:,.0f}', 'masculino': '{:,.0f}', 'total_vitimas': '{:,.0f}', 'perc_feminino': '{:.2f}%', 'perc_masculino': '{:.2f}%'}), use_container_width=True, hide_index=True)

    with subabas_g[3]:
        st.subheader("Análise Histórica e Previsão de Vítimas")
        df_nacional = df[df['Ano'] < 2026].groupby('Ano')[['feminino', 'masculino']].sum().reset_index()
        df_nacional['total_vitimas'] = df_nacional['feminino'] + df_nacional['masculino']
        df_nacional['pct_fem'] = (df_nacional['feminino'] / df_nacional['total_vitimas']) * 100
        df_nacional['pct_masc'] = (df_nacional['masculino'] / df_nacional['total_vitimas']) * 100
        
        X_reg = df_nacional[['Ano']]
        modelo_lr = LinearRegression().fit(X_reg, df_nacional['total_vitimas'])
        modelo_fem = LinearRegression().fit(X_reg, df_nacional['feminino'])
        modelo_masc = LinearRegression().fit(X_reg, df_nacional['masculino'])
        
        anos_futuros = pd.DataFrame({'Ano': [2026, 2027, 2028, 2029, 2030]})
        prev_tot = modelo_lr.predict(anos_futuros)
        prev_masc = modelo_masc.predict(anos_futuros)
        prev_fem = modelo_fem.predict(anos_futuros)
        
        fig_previsao = go.Figure()
        fig_previsao.add_trace(go.Scatter(x=df_nacional['Ano'], y=df_nacional['masculino'], mode='lines+markers+text', name='Histórico Masculino', text=df_nacional['pct_masc'].map('{:.1f}%'.format), textposition='top center'))
        fig_previsao.add_trace(go.Scatter(x=df_nacional['Ano'], y=df_nacional['feminino'], mode='lines+markers+text', name='Histórico Feminino', text=df_nacional['pct_fem'].map('{:.1f}%'.format), textposition='bottom center'))
        fig_previsao.add_trace(go.Scatter(x=list(anos_futuros['Ano']), y=list(prev_tot), mode='lines+markers', name='Previsão Total', line=dict(dash='dot'), marker=dict(symbol='star')))
        fig_previsao.update_layout(title='Tendência e Projeção por Gênero', xaxis=dict(tickmode='linear'), yaxis=dict(title='Quantidade'))
        st.plotly_chart(fig_previsao, use_container_width=True)
        st.divider()
        
        c1, c2, c3, c4, c5 = st.columns(5)
        for idx, col in enumerate([c1, c2, c3, c4, c5]):
            with col:
                st.markdown(f"#### **Ano {2026 + idx}**")
                st.metric("Total", f"{int(prev_tot[idx]):,}")

    with subabas_g[4]:
        st.subheader("Comparação de Modelos: Regressão Linear vs Random Forest vs XGBoost")
        df_ml = df[df['Ano'] < 2026].groupby('Ano')[['feminino', 'masculino']].sum().reset_index()
        df_ml['total_vitimas'] = df_ml['feminino'] + df_ml['masculino']
        X_ml, y_ml = df_ml[['Ano']], df_ml['total_vitimas']
        
        lr, rf, xgb = LinearRegression(), RandomForestRegressor(n_estimators=100, random_state=42), XGBRegressor(n_estimators=100, random_state=42)
        lr.fit(X_ml, y_ml); rf.fit(X_ml, y_ml); xgb.fit(X_ml, y_ml)
        
        def calc_met(y_t, y_p):
            return mean_absolute_error(y_t, y_p), np.sqrt(mean_squared_error(y_t, y_p)), r2_score(y_t, y_p)
            
        m_lr, m_rf, m_xgb = calc_met(y_ml, lr.predict(X_ml)), calc_met(y_ml, rf.predict(X_ml)), calc_met(y_ml, xgb.predict(X_ml))
        df_m = pd.DataFrame({
            'Métrica': ['MAE', 'RMSE', 'R²'],
            'Regressão Linear': [m_lr[0], m_lr[1], m_lr[2]],
            'Random Forest': [m_rf[0], m_rf[1], m_rf[2]],
            'XGBoost': [m_xgb[0], m_xgb[1], m_xgb[2]]
        })
        st.dataframe(df_m.style.format({'Regressão Linear': '{:,.6f}', 'Random Forest': '{:,.6f}', 'XGBoost': '{:,.6f}'}), hide_index=True)