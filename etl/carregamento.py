# arquivo: load.py
import pandas as pd
import os
import time
import tempfile

from database.models import init_db


COLUNAS_COPY = [
    "uf",
    "municipio",
    "evento",
    "data_referencia",
    "agente",
    "arma",
    "faixa_etaria",
    "feminino",
    "masculino",
    "nao_informado",
    "total_vitima",
    "total",
    "total_peso",
    "abrangencia",
]

COLUNAS_INTEGER = [
    "feminino",
    "masculino",
    "nao_informado",
    "total_vitima",
    "total",
]

COLUNAS_FLOAT = [
    "total_peso",
]



def carregar_dados_sinesp(df, nome_tabela, caminho_arquivo):
    extensao = os.path.splitext(caminho_arquivo)[1].lower()

    if df is None or df.empty:
        print("Nenhum dado para inserir.")
        return False

    if extensao not in (".csv", ".xlsx"):
        print(f"Formato não suportado: {extensao}")
        return False

    print(
        f"Carregando {len(df)} registros "
        f"na tabela '{nome_tabela}'..."
    )

    inicio = time.perf_counter()
    caminho_csv = None
    temporario = False

    try:
        # 1. Verifica as colunas
        colunas_faltantes = [
            coluna for coluna in COLUNAS_COPY
            if coluna not in df.columns
        ]

        if colunas_faltantes:
            raise ValueError(
                "Colunas ausentes no DataFrame: "
                + ", ".join(colunas_faltantes)
            )

        # 2. Seleciona as colunas da tabela
        df_copy = df[COLUNAS_COPY].copy()

        # 3. Ajusta os tipos numéricos
        for coluna in COLUNAS_INTEGER:
            df_copy[coluna] = (
                df_copy[coluna].fillna(0).astype(int)
            )

        for coluna in COLUNAS_FLOAT:
            df_copy[coluna] = pd.to_numeric(
                df_copy[coluna], errors="raise"
            )

        # 4. Define o arquivo que será usado pelo COPY
        if extensao == ".csv":
            print("Arquivo já está em CSV. Conversão ignorada.")

            # O CSV original não será removido.
            # O DataFrame transformado será serializado para
            # um CSV temporário compatível com o COPY.
        else:
            print("Arquivo Excel detectado.")

        # O COPY precisa receber os dados transformados.
        # Portanto, geramos um CSV temporário a partir do DataFrame.
        arquivo_temp = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            encoding="utf-8",
            delete=False,
            newline=""
        )
        caminho_csv = arquivo_temp.name
        arquivo_temp.close()
        temporario = True

        df_copy.to_csv(
            caminho_csv,
            index=False,
            sep=",",
            na_rep="",
            encoding="utf-8"
        )

        # 5. Conexão com PostgreSQL
        engine = init_db()

        # 6. COPY para PostgreSQL
        inicio_copy = time.perf_counter()
        conexao = engine.raw_connection()

        try:
            cursor = conexao.cursor()

            colunas_sql = ", ".join(
                f'"{coluna}"' for coluna in COLUNAS_COPY
            )

            comando_copy = f"""
                COPY "{nome_tabela}" ({colunas_sql})
                FROM STDIN
                WITH (
                    FORMAT CSV,
                    HEADER TRUE,
                    DELIMITER ',',
                    NULL ''
                )
            """

            with open(caminho_csv, "rb") as arquivo:
                with cursor.copy(comando_copy) as copy:
                    while True:
                        bloco = arquivo.read(1024 * 1024)
                        if not bloco:
                            break
                        copy.write(bloco)

            conexao.commit()

        except Exception:
            conexao.rollback()
            raise

        finally:
            cursor.close()
            conexao.close()

        fim_copy = time.perf_counter()
        print(f"COPY concluído em {fim_copy - inicio_copy:.2f}s")

        return True

    except Exception as e:
        print(f"Erro durante a carga: {e}")
        return False

    finally:
        # Remove somente o CSV temporário criado pela função.
        if temporario and caminho_csv and os.path.exists(caminho_csv):
            try:
                os.remove(caminho_csv)
            except OSError as e:
                print(f"Aviso: não foi possível remover o temporário: {e}")