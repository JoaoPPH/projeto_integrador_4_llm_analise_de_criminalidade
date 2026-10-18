
import streamlit as st

from services.n8n_client import (
    analisar_criminalidade,
    N8NError,
)


def renderizar_aba_analise_ia(df):
    st.header("Análise personalizada com Inteligência Artificial")

    st.write(
        "Informe o destino e o contexto da sua viagem "
        "para receber recomendações preventivas baseadas "
        "nas estatísticas disponíveis."
    )

    # Aproveita as colunas existentes no DataFrame carregado pelo app.
    ufs = sorted(
        df["uf"].dropna().astype(str).str.upper().unique()
    )

    if not ufs:
        st.warning("Não existem UFs disponíveis na base.")
        return

    uf = st.selectbox("Estado (UF)", ufs)

    municipios = sorted(
        df.loc[
            (df["uf"].astype(str).str.upper() == uf)
            & df["municipio"].notna(),
            "municipio",
        ].astype(str).unique()
    )

    municipios = [
        m for m in municipios
        if m.strip()
        and m.strip().upper() not in {
            "NÃO INFORMADO",
            "NAO INFORMADO",
        }
    ]

    if not municipios:
        st.warning("Nenhum município disponível para essa UF.")
        return

    municipio = st.selectbox("Município de destino", municipios)

    with st.form("form_analise_ia"):
        transporte = st.selectbox(
            "Meio de transporte",
            ["Carro", "Moto", "Transporte público", "A pé", "Outro"],
        )

        acompanhantes = st.selectbox(
            "Acompanhantes",
            ["Sozinho", "Família", "Amigos", "Outro"],
        )

        periodo = st.selectbox(
            "Período",
            ["Manhã", "Tarde", "Noite", "Madrugada", "Vários períodos"],
        )

        objetivo = st.selectbox(
            "Objetivo",
            ["Turismo", "Trabalho", "Estudo", "Moradia", "Outro"],
        )

        enviar = st.form_submit_button(
            "Gerar análise de segurança"
        )

    if enviar:
        try:
            with st.spinner(
                "Consultando os dados e gerando a análise..."
            ):
                resultado = analisar_criminalidade(
                    uf=uf,
                    municipio=municipio,
                    meio_transporte=transporte,
                    acompanhantes=acompanhantes,
                    periodo=periodo,
                    objetivo=objetivo,
                )

            st.subheader("Recomendações personalizadas")
            st.markdown(resultado["analise"])

            with st.expander("Consultar dados utilizados"):
                st.json(resultado.get("dados", {}))

            st.caption(
                f"Modelo utilizado: "
                f"{resultado.get('modelo', 'Não informado')}"
            )

        except (N8NError, ValueError) as exc:
            st.error(str(exc))
