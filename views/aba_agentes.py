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

def renderizar_aba_agentes(df):
    st.header("4. Análise de Risco de Morte por Tipo de Agente")

    st.markdown("#### Filtros da Análise de Morte de Agentes")
    col_uf_p, col_ano_p, col_evento_p = st.columns(3)

    eventos_agente = ['Morte de Agente do Estado', 'Suicidio de Agente do Estado']
    df_agentes_base = df[(df['Ano'] < 2026) & (df['evento'].isin(eventos_agente))].copy()

    with col_uf_p:
        lista_uf_p = sorted(df_agentes_base['uf'].dropna().unique())
        ufs_selecionadas_p = st.multiselect("Filtrar por Estado (UF):", options=lista_uf_p, key="multiselect_uf_p")

    with col_ano_p:
        lista_anos_p = sorted(df_agentes_base['Ano'].unique())
        anos_selecionados_p = st.multiselect("Filtrar por Ano:", options=lista_anos_p, key="multiselect_ano_p")

    with col_evento_p:
        evento_selecionado_p = st.multiselect("Filtrar por Tipo de Evento:", options=eventos_agente, key="multiselect_evento_p")

    df_filtrado_p = df_agentes_base.copy()
    if ufs_selecionadas_p:
        df_filtrado_p = df_filtrado_p[df_filtrado_p['uf'].isin(ufs_selecionadas_p)]
    if anos_selecionados_p:
        df_filtrado_p = df_filtrado_p[df_filtrado_p['Ano'].isin(anos_selecionados_p)]
    if evento_selecionado_p:
        df_filtrado_p = df_filtrado_p[df_filtrado_p['evento'].isin(evento_selecionado_p)]

    subabas_p = st.tabs([
        "Visão Geral de Mortes de Agentes",
        "Evolução Temporal",
        "Análise Geográfica por Estado",
        "Análise de Regressão e Tendências",
        "Comparação de Modelos: Regressão Linear vs Random Forest vs XGBoost"
    ])

    with subabas_p[0]:
        st.subheader("Visão Geral de Mortes e Suicídios de Agentes do Estado")

        total_vitimas_agentes = df_filtrado_p['total_vitima'].sum()
        total_registros_agentes = len(df_filtrado_p)
        tipos_agentes = df_filtrado_p['agente'].dropna().nunique()
        estados_afetados = df_filtrado_p['uf'].dropna().nunique()

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total de Vítimas", f"{int(total_vitimas_agentes):,}")
        m2.metric("Total de Registros", f"{total_registros_agentes:,}")
        m3.metric("Tipos de Agentes", f"{tipos_agentes}")
        m4.metric("Estados com Registros", f"{estados_afetados}")

        st.divider()

        st.markdown("#### Total de Mortes por Tipo de Agente no Brasil")
        mortes_por_agente = (
            df_filtrado_p
            .groupby('agente')['total_vitima']
            .sum()
            .reset_index()
            .sort_values(by='total_vitima', ascending=False)
        )
        total_geral_agentes = mortes_por_agente['total_vitima'].sum()
        mortes_por_agente['Porcentagem (%)'] = np.where(
            total_geral_agentes > 0,
            (mortes_por_agente['total_vitima'] / total_geral_agentes * 100).round(2),
            0
        )
        mortes_por_agente = mortes_por_agente.rename(columns={'total_vitima': 'Total de Vítimas', 'agente': 'Tipo de Agente'})

        fig_agente_bar = px.bar(
            data_frame=mortes_por_agente,
            x='Total de Vítimas',
            y='Tipo de Agente',
            orientation='h',
            title='Total de Mortes por Tipo de Agente',
            color='Total de Vítimas',
            color_continuous_scale='Reds'
        )
        fig_agente_bar.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_agente_bar, width="stretch")

        st.dataframe(
            mortes_por_agente.style.format({
                'Total de Vítimas': '{:,.0f}',
                'Porcentagem (%)': '{:.2f}%'
            }),
            width="stretch",
            hide_index=True
        )

        st.divider()

        st.markdown("#### Top 10 Estados com Mais Mortes de Agentes")
        mortes_total_estado = (
            df_filtrado_p
            .groupby('uf')['total_vitima']
            .sum()
            .reset_index()
            .sort_values(by='total_vitima', ascending=False)
        )

        fig_top_estados = px.bar(
            data_frame=mortes_total_estado.head(10),
            x='uf',
            y='total_vitima',
            title='Top 10 Estados com Mais Mortes de Agentes do Estado',
            labels={'uf': 'Estado', 'total_vitima': 'Total de Vítimas'},
            color='total_vitima',
            color_continuous_scale='Reds'
        )
        fig_top_estados.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_top_estados, width="stretch")

        st.divider()

        st.markdown("#### Tipo de Agente com Maior Número de Mortes por Estado")
        mortes_por_estado_agente = (
            df_filtrado_p
            .groupby(['uf', 'agente'])['total_vitima']
            .sum()
            .reset_index()
        )
        agente_mais_mortes_estado = (
            mortes_por_estado_agente
            .sort_values(['uf', 'total_vitima'], ascending=[True, False])
            .groupby('uf')
            .first()
            .reset_index()
        )
        agente_mais_mortes_estado = agente_mais_mortes_estado.rename(columns={
            'uf': 'Estado',
            'agente': 'Agente com Mais Mortes',
            'total_vitima': 'Total de Vítimas'
        })

        fig_agente_estado = px.bar(
            data_frame=agente_mais_mortes_estado,
            x='Estado',
            y='Total de Vítimas',
            color='Agente com Mais Mortes',
            title='Tipo de Agente com Maior Número de Mortes por Estado',
            labels={'Total de Vítimas': 'Total de Vítimas', 'Estado': 'Estado'}
        )
        fig_agente_estado.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_agente_estado, width="stretch")

        st.dataframe(
            agente_mais_mortes_estado.style.format({
                'Total de Vítimas': '{:,.0f}'
            }),
            width="stretch",
            hide_index=True
        )

    with subabas_p[1]:
        st.subheader("Evolução Temporal de Mortes de Agentes do Estado")

        mortes_brasil_ano = df_filtrado_p.groupby('Ano')['total_vitima'].sum().reset_index()

        fig_evolucao_total = px.line(
            data_frame=mortes_brasil_ano,
            x='Ano',
            y='total_vitima',
            title='Evolução do Total de Mortes de Agentes do Estado no Brasil',
            labels={'Ano': 'Ano', 'total_vitima': 'Total de Vítimas'},
            markers=True
        )
        fig_evolucao_total.update_traces(line=dict(color='darkred', width=3), marker=dict(size=8))
        fig_evolucao_total.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_evolucao_total, width="stretch")

        st.divider()

        st.markdown("#### Evolução de Mortes por Tipo de Agente ao Longo dos Anos")
        mortes_agente_ano = (
            df_filtrado_p
            .groupby(['Ano', 'agente'])['total_vitima']
            .sum()
            .reset_index()
        )

        fig_agente_ano = px.line(
            data_frame=mortes_agente_ano,
            x='Ano',
            y='total_vitima',
            color='agente',
            title='Evolução de Mortes por Tipo de Agente ao Longo dos Anos',
            labels={'Ano': 'Ano', 'total_vitima': 'Total de Vítimas', 'agente': 'Tipo de Agente'},
            markers=True
        )
        fig_agente_ano.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_agente_ano, width="stretch")

        tabela_agente_ano = mortes_agente_ano.pivot(index='Ano', columns='agente', values='total_vitima').fillna(0)
        tabela_agente_ano['Total Geral'] = tabela_agente_ano.sum(axis=1)

        format_dict_agente = {col: '{:,.0f}' for col in tabela_agente_ano.columns}
        st.markdown("#### Detalhamento de Mortes por Tipo de Agente e Ano")
        st.dataframe(
            tabela_agente_ano.style.format(format_dict_agente),
            width="stretch"
        )

        st.divider()

        st.markdown("#### Morte vs Suicídio de Agentes do Estado por Ano")
        mortes_evento_ano = (
            df_filtrado_p
            .groupby(['Ano', 'evento'])['total_vitima']
            .sum()
            .reset_index()
        )

        mapa_cores_evento = {
            'Morte de Agente do Estado': '#b22222',
            'Suicidio de Agente do Estado': '#4682b4'
        }

        fig_evento_ano = px.line(
            data_frame=mortes_evento_ano,
            x='Ano',
            y='total_vitima',
            color='evento',
            title='Morte vs Suicídio de Agentes do Estado por Ano',
            labels={'Ano': 'Ano', 'total_vitima': 'Total de Vítimas', 'evento': 'Tipo de Evento'},
            markers=True,
            color_discrete_map=mapa_cores_evento
        )
        fig_evento_ano.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_evento_ano, width="stretch")

        tabela_evento_ano = mortes_evento_ano.pivot(index='Ano', columns='evento', values='total_vitima').fillna(0)
        tabela_evento_ano['Total'] = tabela_evento_ano.sum(axis=1)

        format_dict_evento = {col: '{:,.0f}' for col in tabela_evento_ano.columns}
        st.dataframe(
            tabela_evento_ano.style.format(format_dict_evento),
            width="stretch"
        )

    with subabas_p[2]:
        st.subheader("Distribuição Geográfica de Mortes de Agentes por Estado")

        @st.cache_data
        def carregar_geojson_agentes():
            url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
            return requests.get(url).json()

        with st.spinner('Carregando mapa interativo...'):
            geojson_agentes = carregar_geojson_agentes()

        df_mapa_agentes = df_filtrado_p.groupby('uf').agg({
            'total_vitima': 'sum'
        }).reset_index()
        df_mapa_agentes['uf'] = df_mapa_agentes['uf'].astype(str).str.upper().str.strip()

        df_morte_uf = df_filtrado_p[df_filtrado_p['evento'] == 'Morte de Agente do Estado'].groupby('uf')['total_vitima'].sum().reset_index()
        df_morte_uf.columns = ['uf', 'mortes']
        df_suicidio_uf = df_filtrado_p[df_filtrado_p['evento'] == 'Suicidio de Agente do Estado'].groupby('uf')['total_vitima'].sum().reset_index()
        df_suicidio_uf.columns = ['uf', 'suicidios']

        df_mapa_agentes = df_mapa_agentes.merge(df_morte_uf, on='uf', how='left').merge(df_suicidio_uf, on='uf', how='left')
        df_mapa_agentes['mortes'] = df_mapa_agentes['mortes'].fillna(0)
        df_mapa_agentes['suicidios'] = df_mapa_agentes['suicidios'].fillna(0)

        df_mapa_agentes['perc_mortes'] = np.where(
            df_mapa_agentes['total_vitima'] > 0,
            (df_mapa_agentes['mortes'] / df_mapa_agentes['total_vitima'] * 100).round(2),
            0
        )
        df_mapa_agentes['perc_suicidios'] = np.where(
            df_mapa_agentes['total_vitima'] > 0,
            (df_mapa_agentes['suicidios'] / df_mapa_agentes['total_vitima'] * 100).round(2),
            0
        )

        fig_mapa_agentes = px.choropleth(
            data_frame=df_mapa_agentes,
            geojson=geojson_agentes,
            locations='uf',
            featureidkey="properties.sigla",
            color='total_vitima',
            hover_name='uf',
            hover_data={
                'uf': False,
                'total_vitima': ':,',
                'mortes': ':,',
                'suicidios': ':,',
                'perc_mortes': ':.2f',
                'perc_suicidios': ':.2f'
            },
            title='<b>Distribuição de Mortes de Agentes do Estado por UF (Mapa Interativo)</b>',
            color_continuous_scale="Reds",
            labels={
                'total_vitima': 'Total de Vítimas',
                'mortes': 'Mortes em Serviço',
                'suicidios': 'Suicídios',
                'perc_mortes': 'Mortes (%)',
                'perc_suicidios': 'Suicídios (%)'
            }
        )
        fig_mapa_agentes.update_geos(fitbounds="locations", visible=False)
        fig_mapa_agentes.update_layout(
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            height=600,
            template="plotly_white"
        )
        st.plotly_chart(fig_mapa_agentes, width="stretch")

        st.divider()

        st.markdown("#### Dados Consolidados por Unidade da Federação:")
        st.dataframe(
            df_mapa_agentes.sort_values(by='total_vitima', ascending=False).style.format({
                'total_vitima': '{:,.0f}',
                'mortes': '{:,.0f}',
                'suicidios': '{:,.0f}',
                'perc_mortes': '{:.2f}%',
                'perc_suicidios': '{:.2f}%'
            }),
            width="stretch",
            hide_index=True
        )

    with subabas_p[3]:
        st.subheader("Análise de Regressão e Tendências de Mortes de Agentes")
        st.write("Esta seção executa modelos de Regressão Linear para identificar tendências nacionais, estaduais e por tipo de agente, projetando os próximos anos.")

        df_nacional_ag = df_agentes_base.groupby('Ano')['total_vitima'].sum().reset_index()

        X_reg_ag = df_nacional_ag[['Ano']]
        y_reg_ag = df_nacional_ag['total_vitima']
        modelo_ag = LinearRegression()
        modelo_ag.fit(X_reg_ag, y_reg_ag)

        y_pred_hist_ag = modelo_ag.predict(X_reg_ag)

        anos_futuros_ag = pd.DataFrame({'Ano': [2026, 2027, 2028, 2029, 2030]})
        previsoes_ag = modelo_ag.predict(anos_futuros_ag)

        r2_ag = r2_score(y_reg_ag, y_pred_hist_ag)
        mae_ag = mean_absolute_error(y_reg_ag, y_pred_hist_ag)

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Coeficiente (Inclinação)", f"{modelo_ag.coef_[0]:.2f}")
        col_r2.metric("R² (Determinação)", f"{r2_ag:.4f}")
        col_r3.metric("MAE (Erro Médio Absoluto)", f"{mae_ag:,.2f}")

        fig_regressao_ag = go.Figure()

        fig_regressao_ag.add_trace(go.Scatter(
            x=df_nacional_ag['Ano'],
            y=df_nacional_ag['total_vitima'],
            mode='lines+markers',
            name='Dados Reais',
            line=dict(color='darkred', width=2),
            marker=dict(size=8)
        ))

        fig_regressao_ag.add_trace(go.Scatter(
            x=df_nacional_ag['Ano'],
            y=y_pred_hist_ag,
            mode='lines',
            name='Reta Ajustada',
            line=dict(color='red', width=1.5, dash='dash')
        ))

        fig_regressao_ag.add_trace(go.Scatter(
            x=list(anos_futuros_ag['Ano']),
            y=list(previsoes_ag),
            mode='lines+markers',
            name='Previsão (2026-2030)',
            line=dict(color='green', width=2.5, dash='dot'),
            marker=dict(size=10, symbol='star')
        ))

        fig_regressao_ag.update_layout(
            title='Regressão Linear - Mortes de Agentes do Estado no Brasil',
            xaxis=dict(title='Ano', tickmode='linear'),
            yaxis=dict(title='Total de Vítimas'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified',
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_regressao_ag, width="stretch")

        st.divider()
        st.markdown("### Métricas Projetadas (2026 - 2030)")

        c1, c2, c3, c4, c5 = st.columns(5)
        anos_lista_ag = [2026, 2027, 2028, 2029, 2030]
        colunas_lista_ag = [c1, c2, c3, c4, c5]

        for idx, col in enumerate(colunas_lista_ag):
            with col:
                st.markdown(f"#### **Ano {anos_lista_ag[idx]}**")
                st.metric("Total Projetado", f"{int(previsoes_ag[idx]):,}")

        st.divider()

        st.markdown("### Tendência de Mortes por Estado (Coeficiente da Regressão)")
        resultados_estado_ag = []

        for estado in df_agentes_base['uf'].unique():
            dados_est = (
                df_agentes_base[df_agentes_base['uf'] == estado]
                .groupby('Ano')['total_vitima']
                .sum()
                .reset_index()
            )

            if len(dados_est) > 1:
                X_est = dados_est[['Ano']]
                y_est = dados_est['total_vitima']
                modelo_est = LinearRegression()
                modelo_est.fit(X_est, y_est)
                coef_est = modelo_est.coef_[0]
                prev_2027 = modelo_est.predict(pd.DataFrame({'Ano': [2027]}))[0]

                if coef_est > 0:
                    tendencia = 'Aumento'
                elif coef_est < 0:
                    tendencia = 'Diminuição'
                else:
                    tendencia = 'Estável'

                resultados_estado_ag.append([estado, coef_est, prev_2027, tendencia])

        df_tendencia_estado_ag = pd.DataFrame(
            resultados_estado_ag,
            columns=['Estado', 'Coeficiente', 'Previsão 2027', 'Tendência']
        )
        df_tend_sorted_ag = df_tendencia_estado_ag.sort_values('Coeficiente', ascending=False)

        df_tend_sorted_ag['Cor'] = df_tend_sorted_ag['Coeficiente'].apply(
            lambda c: 'Aumento' if c > 0 else ('Diminuição' if c < 0 else 'Estável')
        )

        mapa_cores_tend = {
            'Aumento': '#b22222',
            'Diminuição': '#4682b4',
            'Estável': '#808080'
        }

        fig_tendencia_estado = px.bar(
            data_frame=df_tend_sorted_ag,
            x='Estado',
            y='Coeficiente',
            color='Cor',
            color_discrete_map=mapa_cores_tend,
            title='Tendência de Mortes de Agentes por Estado (Coeficiente da Regressão Linear)',
            labels={'Coeficiente': 'Coeficiente (positivo = aumento)', 'Estado': 'Estado', 'Cor': 'Tendência'}
        )
        fig_tendencia_estado.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_tendencia_estado, width="stretch")

        st.dataframe(
            df_tend_sorted_ag[['Estado', 'Coeficiente', 'Previsão 2027', 'Tendência']].style.format({
                'Coeficiente': '{:.4f}',
                'Previsão 2027': '{:,.0f}'
            }),
            width="stretch",
            hide_index=True
        )

        st.divider()

        st.markdown("### Resumo: Estados com Aumento vs Diminuição")
        contagem_tend = df_tendencia_estado_ag['Tendência'].value_counts().reset_index()
        contagem_tend.columns = ['Tendência', 'Quantidade de Estados']

        fig_resumo_tend = px.bar(
            data_frame=contagem_tend,
            x='Tendência',
            y='Quantidade de Estados',
            color='Tendência',
            color_discrete_map=mapa_cores_tend,
            title='Quantidade de Estados por Tendência de Mortes de Agentes'
        )
        st.plotly_chart(fig_resumo_tend, width="stretch")

        st.divider()

        st.markdown("### Tendência por Estado e Tipo de Agente")
        resultados_estado_agente_ag = []

        for estado in df_agentes_base['uf'].unique():
            for agente in df_agentes_base['agente'].dropna().unique():
                dados_ea = (
                    df_agentes_base[
                        (df_agentes_base['uf'] == estado) &
                        (df_agentes_base['agente'] == agente)
                    ]
                    .groupby('Ano')['total_vitima']
                    .sum()
                    .reset_index()
                )

                if len(dados_ea) > 1:
                    X_ea = dados_ea[['Ano']]
                    y_ea = dados_ea['total_vitima']
                    modelo_ea = LinearRegression()
                    modelo_ea.fit(X_ea, y_ea)
                    coef_ea = modelo_ea.coef_[0]
                    prev_2027_ea = modelo_ea.predict(pd.DataFrame({'Ano': [2027]}))[0]

                    if coef_ea > 0:
                        tend_ea = 'Aumento'
                    elif coef_ea < 0:
                        tend_ea = 'Diminuição'
                    else:
                        tend_ea = 'Estável'

                    resultados_estado_agente_ag.append([estado, agente, coef_ea, prev_2027_ea, tend_ea])

        df_tend_estado_agente = pd.DataFrame(
            resultados_estado_agente_ag,
            columns=['Estado', 'Agente', 'Coeficiente', 'Previsão 2027', 'Tendência']
        )

        aumento_agente_estado = (
            df_tend_estado_agente[df_tend_estado_agente['Coeficiente'] > 0]
            .sort_values(by='Coeficiente', ascending=False)
            .groupby('Estado')
            .first()
            .reset_index()
        )

        diminuicao_agente_estado = (
            df_tend_estado_agente[df_tend_estado_agente['Coeficiente'] < 0]
            .sort_values(by='Coeficiente', ascending=True)
            .groupby('Estado')
            .first()
            .reset_index()
        )

        if len(aumento_agente_estado) > 0:
            st.markdown("#### Tipo de Agente com Maior Tendência de Aumento por Estado")
            aumento_agente_estado['Descrição'] = aumento_agente_estado['Estado'] + ' - ' + aumento_agente_estado['Agente']

            fig_aumento = px.bar(
                data_frame=aumento_agente_estado.sort_values('Coeficiente', ascending=False),
                x='Descrição',
                y='Coeficiente',
                title='Tipo de Agente com Maior Tendência de Aumento de Mortes por Estado',
                labels={'Descrição': 'Estado - Agente', 'Coeficiente': 'Coeficiente'},
                color_discrete_sequence=['#b22222']
            )
            fig_aumento.update_layout(xaxis=dict(tickangle=90))
            st.plotly_chart(fig_aumento, width="stretch")

        if len(diminuicao_agente_estado) > 0:
            st.markdown("#### Tipo de Agente com Maior Tendência de Diminuição por Estado")
            diminuicao_agente_estado['Descrição'] = diminuicao_agente_estado['Estado'] + ' - ' + diminuicao_agente_estado['Agente']

            fig_diminuicao = px.bar(
                data_frame=diminuicao_agente_estado.sort_values('Coeficiente', ascending=True),
                x='Descrição',
                y='Coeficiente',
                title='Tipo de Agente com Maior Tendência de Diminuição de Mortes por Estado',
                labels={'Descrição': 'Estado - Agente', 'Coeficiente': 'Coeficiente'},
                color_discrete_sequence=['#4682b4']
            )
            fig_diminuicao.update_layout(xaxis=dict(tickangle=90))
            st.plotly_chart(fig_diminuicao, width="stretch")

        st.divider()

        st.markdown("### Tabela Resumo: Maior Aumento e Diminuição por Estado")
        resumo_agentes = aumento_agente_estado[['Estado', 'Agente', 'Coeficiente']].merge(
            diminuicao_agente_estado[['Estado', 'Agente', 'Coeficiente']],
            on='Estado',
            how='outer',
            suffixes=('_Aumento', '_Diminuição')
        )
        st.dataframe(
            resumo_agentes.style.format({
                'Coeficiente_Aumento': '{:.4f}',
                'Coeficiente_Diminuição': '{:.4f}'
            }),
            width="stretch",
            hide_index=True
        )

    with subabas_p[4]:
        st.subheader("Comparação de Modelos: Regressão Linear vs Random Forest vs XGBoost")

        df_ml_ag = df_agentes_base.groupby('Ano')['total_vitima'].sum().reset_index()
        X_ml_ag = df_ml_ag[['Ano']]
        y_ml_ag = df_ml_ag['total_vitima']

        lr_ag = LinearRegression()
        rf_ag = RandomForestRegressor(n_estimators=100, random_state=42)
        xgb_ag = XGBRegressor(n_estimators=100, random_state=42)

        lr_ag.fit(X_ml_ag, y_ml_ag)
        rf_ag.fit(X_ml_ag, y_ml_ag)
        xgb_ag.fit(X_ml_ag, y_ml_ag)

        y_pred_lr_ag = lr_ag.predict(X_ml_ag)
        y_pred_rf_ag = rf_ag.predict(X_ml_ag)
        y_pred_xgb_ag = xgb_ag.predict(X_ml_ag)

        def calcular_metricas(y_true, y_pred):
            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            r2 = r2_score(y_true, y_pred)
            return mae, rmse, r2

        m_lr_ag = calcular_metricas(y_ml_ag, y_pred_lr_ag)
        m_rf_ag = calcular_metricas(y_ml_ag, y_pred_rf_ag)
        m_xgb_ag = calcular_metricas(y_ml_ag, y_pred_xgb_ag)

        df_metricas_ag = pd.DataFrame({
            'Métrica': ['MAE (Erro Médio Absoluto)', 'RMSE (Raiz do Erro Quadrático Médio)', 'R² (Coef. de Determinação)'],
            'Regressão Linear': [m_lr_ag[0], m_lr_ag[1], m_lr_ag[2]],
            'Random Forest': [m_rf_ag[0], m_rf_ag[1], m_rf_ag[2]],
            'XGBoost': [m_xgb_ag[0], m_xgb_ag[1], m_xgb_ag[2]]
        })

        st.markdown("#### Métricas de Performance Computadas na Base Histórica:")
        st.dataframe(df_metricas_ag.style.format({
            'Regressão Linear': '{:,.6f}',
            'Random Forest': '{:,.6f}',
            'XGBoost': '{:,.6f}'
        }),
            hide_index=True
        )

        st.divider()

        df_ajuste_ag = pd.DataFrame({
            'Ano': df_ml_ag['Ano'],
            'Real': y_ml_ag,
            'Regr. Linear': y_pred_lr_ag,
            'Random Forest': y_pred_rf_ag,
            'XGBoost': y_pred_xgb_ag
        })
        fig_comp_ag = px.line(
            data_frame=df_ajuste_ag,
            x='Ano',
            y=['Real', 'Regr. Linear', 'Random Forest', 'XGBoost'],
            title='Comparação do Ajuste dos Modelos à Curva Real Histórica',
            markers=True
        )
        fig_comp_ag.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_comp_ag, width="stretch")

        st.divider()

        st.markdown("### Projeções Futuras por Modelo (2026-2030)")
        anos_futuros_ml = pd.DataFrame({'Ano': [2026, 2027, 2028, 2029, 2030]})
        prev_lr_fut = lr_ag.predict(anos_futuros_ml)
        prev_rf_fut = rf_ag.predict(anos_futuros_ml)
        prev_xgb_fut = xgb_ag.predict(anos_futuros_ml)

        df_proj_modelos = pd.DataFrame({
            'Ano': anos_futuros_ml['Ano'],
            'Regressão Linear': prev_lr_fut,
            'Random Forest': prev_rf_fut,
            'XGBoost': prev_xgb_fut
        })

        fig_proj_modelos = px.line(
            data_frame=df_proj_modelos,
            x='Ano',
            y=['Regressão Linear', 'Random Forest', 'XGBoost'],
            title='Projeções Futuras de Mortes de Agentes por Modelo (2026-2030)',
            markers=True
        )
        fig_proj_modelos.update_layout(xaxis=dict(tickmode='linear'))
        st.plotly_chart(fig_proj_modelos, width="stretch")

        st.dataframe(
            df_proj_modelos.style.format({
                'Regressão Linear': '{:,.0f}',
                'Random Forest': '{:,.0f}',
                'XGBoost': '{:,.0f}'
            }),
            hide_index=True
        )