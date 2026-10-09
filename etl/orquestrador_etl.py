
# ficheiro: orquestrador_etl.py

import os

from sqlalchemy import text

from .extracao_dados import extrair_dados_sinesp
from .transformacao_dados import transformar_dados_sinesp
from .carregamento import carregar_dados_sinesp

from database.models import (
    OcorrenciaCriminal,
    aplicar_indexes,
    init_db,
)


def listar_arquivos_para_processar(pasta):
    """
    Lista CSVs e Excels, priorizando CSV quando ambos
    possuem o mesmo nome-base.
    """
    escolhidos = {}

    for nome in os.listdir(pasta):
        caminho = os.path.join(pasta, nome)

        if not os.path.isfile(caminho):
            continue

        extensao = os.path.splitext(nome)[1].lower()

        if extensao not in (".csv", ".xlsx"):
            continue

        nome_base = os.path.splitext(nome)[0].casefold()

        atual = escolhidos.get(nome_base)

        # CSV tem prioridade sobre XLSX.
        if atual is None or extensao == ".csv":
            escolhidos[nome_base] = nome

    return sorted(escolhidos.values(), key=str.casefold)


def arquivos_ja_baixados(pasta):
    """
    Verifica se existe pelo menos um arquivo suportado.
    Atenção: isso não garante que todos os anos estejam presentes.
    """
    if not os.path.isdir(pasta):
        return False

    return any(
        os.path.isfile(os.path.join(pasta, nome))
        and os.path.splitext(nome)[1].lower() in (".csv", ".xlsx")
        for nome in os.listdir(pasta)
    )


def executar_pipeline():
    url_fonte = (
        "https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/"
        "seguranca-publica/estatistica/download/dnsp-base-de-dados/"
    )

    pasta_dados = os.getenv("PASTA_DADOS", "./dados_brutos")
    nome_tabela = OcorrenciaCriminal.__tablename__

    engine = init_db()

    try:
        # 1. Extração
        if arquivos_ja_baixados(pasta_dados):
            print(
                "Arquivos locais encontrados. "
                "Pulando a fase de extração."
            )
            pasta_ficheiros = pasta_dados
        else:
            pasta_ficheiros = extrair_dados_sinesp(
                url_fonte,
                pasta_dados
            )

        if not pasta_ficheiros or not os.path.isdir(pasta_ficheiros):
            raise RuntimeError(
                "Processo abortado: pasta de arquivos não encontrada."
            )

        # 2. Seleciona os arquivos, priorizando CSVs.
        arquivos = listar_arquivos_para_processar(pasta_ficheiros)

        if not arquivos:
            raise RuntimeError(
                "Nenhum arquivo CSV ou XLSX encontrado."
            )

        print(f"Arquivos selecionados para processamento: {len(arquivos)}")

        falhas = []

        # 3. Transformação e carga
        for nome_ficheiro in arquivos:
            caminho_completo = os.path.join(
                pasta_ficheiros,
                nome_ficheiro
            )

            print(f"\nProcessando: {nome_ficheiro}")

            try:
                df_tratado = transformar_dados_sinesp(
                    caminho_completo
                )

                if df_tratado is None or df_tratado.empty:
                    print(
                        f"Falha ou ausência de dados em "
                        f"{nome_ficheiro}."
                    )
                    falhas.append(nome_ficheiro)
                    continue

                sucesso = carregar_dados_sinesp(
                    df_tratado,
                    nome_tabela,
                    caminho_completo
                )

                if not sucesso:
                    falhas.append(nome_ficheiro)
                    print(f"Falha na carga de {nome_ficheiro}.")

            except Exception as erro:
                print(
                    f"Erro ao processar {nome_ficheiro}: {erro}"
                )
                falhas.append(nome_ficheiro)

        # Não declarar sucesso se algum arquivo falhou.
        if falhas:
            print("\nPipeline concluído com falhas.")
            print("Arquivos que falharam:")

            for nome in falhas:
                print(f"- {nome}")

            return

        # 4. Cria índices somente após todas as cargas.
        aplicar_indexes(engine, nome_tabela)

        # 5. Atualiza estatísticas do PostgreSQL.
        with engine.begin() as conn:
            conn.execute(
                text(f'ANALYZE "{nome_tabela}"')
            )

        print("\nPipeline ETL concluído com sucesso.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    executar_pipeline()