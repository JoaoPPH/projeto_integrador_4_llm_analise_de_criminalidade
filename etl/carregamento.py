# arquivo: load.py

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


def carregar_dados_sinesp(df, nome_tabela):

    if df is None or df.empty:
        print("Nenhum dado para inserir.")
        return False

    print(
        f"Carregando {len(df)} registros "
        f"na tabela '{nome_tabela}'..."
    )

    inicio = time.perf_counter()
    caminho_csv = None

    try:
        # ---------------------------------------------------------
        # 1. Verifica se as colunas esperadas existem
        # ---------------------------------------------------------
        colunas_faltantes = [
            coluna
            for coluna in COLUNAS_COPY
            if coluna not in df.columns
        ]

        if colunas_faltantes:
            raise ValueError(
                "Colunas ausentes no DataFrame: "
                + ", ".join(colunas_faltantes)
            )

        # Mantém somente as colunas que serão carregadas.
        # A coluna 'id' não entra: o PostgreSQL irá gerá-la.
        df_copy = df[COLUNAS_COPY]

        # ---------------------------------------------------------
        # 2. Cria conexão
        # ---------------------------------------------------------
        engine = init_db()

        # ---------------------------------------------------------
        # 3. Cria CSV temporário
        # ---------------------------------------------------------
        inicio_csv = time.perf_counter()

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            encoding="utf-8",
            newline=""
        ) as arquivo_temp:

            caminho_csv = arquivo_temp.name

            df_copy.to_csv(
                arquivo_temp,
                index=False,
                header=True,
                na_rep=""
            )

        fim_csv = time.perf_counter()

        print(
            f"CSV temporário criado em "
            f"{fim_csv - inicio_csv:.2f}s"
        )

        # ---------------------------------------------------------
        # 4. COPY para PostgreSQL
        # ---------------------------------------------------------
        inicio_copy = time.perf_counter()

        conexao = engine.raw_connection()

        try:
            cursor = conexao.cursor()

            colunas_sql = ", ".join(COLUNAS_COPY)

            comando_copy = f"""
                COPY {nome_tabela} ({colunas_sql})
                FROM STDIN
                WITH (
                    FORMAT CSV,
                    HEADER TRUE,
                    DELIMITER ',',
                    NULL ''
                )
            """

            with open(
                caminho_csv,
                "rb"
            ) as arquivo:

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

        print(
            f"COPY concluído em "
            f"{fim_copy - inicio_copy:.2f}s"
        )

        # ---------------------------------------------------------
        # 5. Remove CSV temporário
        # ---------------------------------------------------------
        os.remove(caminho_csv)
        caminho_csv = None

        fim = time.perf_counter()

        print("\n" + "=" * 60)
        print(
            f"Carga concluída em "
            f"{fim - inicio:.2f}s"
        )
        print(
            f"Tempo total: "
            f"{(fim - inicio) / 60:.2f} minutos"
        )
        print("=" * 60 + "\n")

        return True

    except Exception as e:

        if caminho_csv and os.path.exists(caminho_csv):
            try:
                os.remove(caminho_csv)
            except OSError:
                pass

        print(f"Erro durante a carga: {e}\n")

        return False