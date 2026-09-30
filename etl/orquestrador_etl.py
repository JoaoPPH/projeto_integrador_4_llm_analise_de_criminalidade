# ficheiro: orquestrador_etl.py
import os
from extracao_dados import extrair_dados_sinesp
from transformacao_dados import transformar_dados_sinesp
from carregamento import carregar_dados_sinesp
from dotenv import load_dotenv

# Lê o ficheiro .env e carrega as variáveis para a memória
load_dotenv()

def executar_pipeline():
    url_fonte = "https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados/"
    pasta_dados = os.getenv("PASTA_DADOS", "./dados_brutos")
    string_conexao = os.getenv("STRING_CONEXAO", "sqlite:///banco_sinesp_local.db")
    nome_tabela = "criminalidade_historico"

    # 1. Extraction
    pasta_ficheiros = extrair_dados_sinesp(url_fonte, pasta_dados)
    
    if not pasta_ficheiros:
        print("Processo abortado na fase de extração.")
        return

    # 2. Transform e 3. Load (ficheiro a ficheiro)
    for nome_ficheiro in os.listdir(pasta_ficheiros):
        if nome_ficheiro.endswith('.xlsx') or nome_ficheiro.endswith('.csv'):
            caminho_completo = os.path.join(pasta_ficheiros, nome_ficheiro)
            
            # Transform
            df_tratado = transformar_dados_sinesp(caminho_completo)
            
            # Load
            if df_tratado is not None and not df_tratado.empty:
                carregar_dados_sinesp(df_tratado, nome_tabela, string_conexao)
            else:
                print(f"Sem dados válidos para carregar provenientes do ficheiro {nome_ficheiro}.")


if __name__ == "__main__":
    executar_pipeline()