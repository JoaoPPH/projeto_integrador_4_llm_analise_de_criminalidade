# ficheiro: orquestrador_etl.py
import os
from .extracao_dados import extrair_dados_sinesp
from .transformacao_dados import transformar_dados_sinesp
from .carregamento import carregar_dados_sinesp
from database.models import OcorrenciaCriminal

def executar_pipeline():
    url_fonte = "https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados/"
    pasta_dados = os.getenv("PASTA_DADOS", "./dados_brutos")
    nome_tabela = OcorrenciaCriminal.__tablename__  # Obtém o nome da tabela a partir do modelo

    # 1. Extraction
    if arquivos_ja_baixados(pasta_dados):
        print("Arquivos já foram baixados anteriormente. Pulando a fase de extração.")
        pasta_ficheiros = pasta_dados
    else:
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
                carregar_dados_sinesp(df_tratado, nome_tabela)
            else:
                print(f"Sem dados válidos para carregar provenientes do ficheiro {nome_ficheiro}.")

def arquivos_ja_baixados(pasta):
    if os.path.exists(pasta):
        arquivos = [f for f in os.listdir(pasta) if f.endswith('.xlsx')]
        if len(arquivos) > 0:  # Pode ajustar para == 12 se quiser exigir todos
            return True
    return False

if __name__ == "__main__":
    executar_pipeline()