import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

def renderizar_aba_geral(df):
    st.header("1. Análise do número de crimes em cada Estado/Município")
    st.markdown("#### Filtros da Análise Geral")

    col_uf_t, col_ano_t = st.columns(2)

    with col_uf_t:
        lista_uf_t = sorted(df['uf'].dropna().unique())
        ufs_selecionadas_t = st.multiselect(
            "Filtrar por Estado (UF):",
            options=lista_uf_t,
            key="multiselect_uf_t"
        )

    with col_ano_t:
        lista_anos_t = sorted(df[df['Ano'] < 2026]['Ano'].dropna().unique())
        anos_selecionados_t = st.multiselect(
            "Filtrar por Ano:",
            options=lista_anos_t,
            key="multiselect_ano_t"
        )

    df_filtrado_t = df[df['Ano'] < 2026].copy()

    if ufs_selecionadas_t:
        df_filtrado_t = df_filtrado_t[df_filtrado_t['uf'].isin(ufs_selecionadas_t)]

    if anos_selecionados_t:
        df_filtrado_t = df_filtrado_t[df_filtrado_t['Ano'].isin(anos_selecionados_t)]

    st.divider()

    subabas_t = st.tabs([
        "Crimes por Estado",
        "Crimes por Município",
        "Crime mais frequente por Estado",
        "Evolução",
        "Regressão Linear e Previsões"
    ])

    with subabas_t[0]:
        st.subheader("Quantidade de Crimes por Estado")
        df_crimes_estado = (
            df_filtrado_t.groupby("uf")["total"]
            .sum()
            .reset_index()
            .sort_values(by="total", ascending=False)
        )
        fig_crimes_estado = px.bar(
            df_crimes_estado, x="uf", y="total",
            title="Total de Ocorrências por Estado",
            labels={"uf": "Estado (UF)", "total": "Total de Ocorrências"},
            text="total", color="total", color_continuous_scale="Blues"
        )
        fig_crimes_estado.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        st.plotly_chart(fig_crimes_estado, use_container_width=True)
        st.divider()
        st.dataframe(
            df_crimes_estado.rename(columns={"uf": "Estado", "total": "Total de Ocorrências"})
            .style.format({"Total de Ocorrências": "{:,.0f}"}),
            use_container_width=True, hide_index=True
        )

    with subabas_t[1]:
        st.subheader("Top 20 Municípios com Mais Ocorrências")
        df_municipios = (
            df_filtrado_t[(df_filtrado_t["municipio"].notna()) & (df_filtrado_t["municipio"] != "NÃO INFORMADO")]
            .groupby("municipio")["total"]
            .sum().reset_index()
            .sort_values(by="total", ascending=False).head(20)
        )
        fig_municipios = px.bar(
            df_municipios, x="total", y="municipio", orientation="h",
            title="Top 20 Municípios com Maior Número de Ocorrências",
            color="total", color_continuous_scale="Oranges"
        )
        fig_municipios.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_municipios, use_container_width=True)
        st.divider()
        st.dataframe(
            df_municipios.rename(columns={"municipio": "Município", "total": "Total de Ocorrências"})
            .style.format({"Total de Ocorrências": "{:,.0f}"}),
            use_container_width=True, hide_index=True
        )

    with subabas_t[2]:
        st.subheader("Crime Mais Frequente em Cada Estado")
        eventos_remover = ["Realização de vistorias", "Atendimento pré-hospitalar", "Emissão de Alvarás de licença", "Busca e salvamento", "Combate a incêndios"]
        df_crimes_validos = df_filtrado_t[~df_filtrado_t["evento"].isin(eventos_remover)].copy()
        df_estado_evento = df_crimes_validos.groupby(["uf", "evento"])["total"].sum().reset_index()
        df_crime_mais_frequente = df_estado_evento.sort_values(["uf", "total"], ascending=[True, False]).groupby("uf").head(1).sort_values(by="total", ascending=False)
        
        fig_crime_estado = px.bar(df_crime_mais_frequente, x="uf", y="total", color="evento", title="Crime Mais Frequente por Estado", text="total")
        fig_crime_estado.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        st.plotly_chart(fig_crime_estado, use_container_width=True)
        st.divider()
        st.dataframe(
            df_crime_mais_frequente.rename(columns={"uf": "Estado", "evento": "Crime mais frequente", "total": "Total de Ocorrências"})
            .style.format({"Total de Ocorrências": "{:,.0f}"}),
            use_container_width=True, hide_index=True
        )

    with subabas_t[3]:
        st.subheader("Evolução Histórica das Ocorrências Criminais")
        df_historico = df_filtrado_t.groupby("Ano")["total"].sum().reset_index().sort_values("Ano")
        fig_historico = px.line(df_historico, x="Ano", y="total", title="Evolução do Número de Ocorrências", markers=True)
        fig_historico.update_layout(xaxis=dict(tickmode="linear", dtick=1))
        st.plotly_chart(fig_historico, use_container_width=True)
        st.divider()
        st.dataframe(
            df_historico.rename(columns={"total": "Total de Ocorrências"})
            .style.format({"Total de Ocorrências": "{:,.0f}"}),
            use_container_width=True, hide_index=True
        )

    with subabas_t[4]:
        st.subheader("Regressão Linear e Previsões para o Sudeste")
        opcoes_regressao = {
            "Espírito Santo - Tráfico de drogas": ("ES", "Tráfico de drogas"),
            "São Paulo - Furto de veículo": ("SP", "Furto de veículo"),
            "Rio de Janeiro - Roubo de veículo": ("RJ", "Roubo de veículo"),
            "Minas Gerais - Furto de veículo": ("MG", "Furto de veículo")
        }
        escolha_regressao = st.selectbox("Selecione a análise:", options=list(opcoes_regressao.keys()), key="select_regressao_thais")
        uf_escolhida, crime_escolhido = opcoes_regressao[escolha_regressao]

        df_regressao = df[(df["uf"] == uf_escolhida) & (df["evento"] == crime_escolhido) & (df["Ano"] < 2026)].copy()
        df_regressao_ano = df_regressao.groupby("Ano")["total"].sum().reset_index().sort_values("Ano")

        if len(df_regressao_ano) < 2:
            st.warning("Não há dados suficientes para calcular a regressão linear.")
        else:
            X = df_regressao_ano[["Ano"]]
            y = df_regressao_ano["total"]
            modelo = LinearRegression()
            modelo.fit(X, y)
            df_regressao_ano["Reta Ajustada"] = modelo.predict(X)
            anos_futuros = pd.DataFrame({"Ano": [2027, 2028, 2029]})
            previsoes = modelo.predict(anos_futuros)
            coeficiente = modelo.coef_[0]
            tendencia = "Aumento" if coeficiente > 0 else ("Diminuição" if coeficiente < 0 else "Estável")

            c1, c2, c3 = st.columns(3)
            c1.markdown("**Estado analisado**"); c1.write(uf_escolhida)
            c2.markdown("**Crime analisado**"); c2.write(crime_escolhido)
            c3.markdown("**Tendência**"); c3.write(tendencia)
            st.metric("Coeficiente da Regressão", f"{coeficiente:,.2f}")

            fig_regressao = go.Figure()
            fig_regressao.add_trace(go.Scatter(x=df_regressao_ano["Ano"], y=df_regressao_ano["total"], mode="lines+markers", name="Histórico Real"))
            fig_regressao.add_trace(go.Scatter(x=df_regressao_ano["Ano"], y=df_regressao_ano["Reta Ajustada"], mode="lines", name="Reta Ajustada", line=dict(dash="dash")))
            fig_regressao.add_trace(go.Scatter(x=anos_futuros["Ano"], y=previsoes, mode="lines+markers", name="Previsão 2027-2029", line=dict(dash="dot")))
            fig_regressao.update_layout(title=f"Regressão Linear - {crime_escolhido} em {uf_escolhida}", xaxis_title="Ano", yaxis_title="Total de Ocorrências", height=600)
            st.plotly_chart(fig_regressao, use_container_width=True)
            st.divider()
            df_previsoes = pd.DataFrame({"Ano": anos_futuros["Ano"], "Previsão": previsoes})
            st.dataframe(df_previsoes.style.format({"Previsão": "{:,.0f}"}), use_container_width=True, hide_index=True)