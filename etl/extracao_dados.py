# arquivo: extract.py
import os
import requests
from bs4 import BeautifulSoup

def extrair_dados_sinesp(url, pasta_destino):
    """Acessa a URL, busca arquivos .xlsx e .csv e faz o download."""
    os.makedirs(pasta_destino, exist_ok=True)
    print("Acessando a página de extração...")
    
    try:
        ano = 2015
        arquivos_baixados = 0
        
        while ano <= 2026:
            link = url + f"bancovde-{ano}.xlsx" + "/@@download/file"  # Atualiza o link para o próximo ano
            nome_arquivo = f"bancovde-{ano}.xlsx"
            
            print(f"Procurando arquivo para o ano {ano}...")
            arquivo_response = requests.get(link)

            if arquivo_response.status_code == 200: 
                print(f"Download concluído: {nome_arquivo}")
                caminho_completo = os.path.join(pasta_destino, nome_arquivo)
 
                with open(caminho_completo, 'wb') as f:
                    f.write(arquivo_response.content)
                arquivos_baixados += 1   
            else:
                print(f"Falha no download do arquivo {nome_arquivo}: {arquivo_response.status_code}")
                break
        
            ano += 1  # Incrementa o ano para a próxima iteração
                
        print(f"Extração concluída! {arquivos_baixados} arquivos baixados.")
        return pasta_destino
        
    except Exception as e:
        print(f"Erro durante a extração: {e}")
        return None

# Se quiser testar o arquivo isoladamente:
if __name__ == "__main__":
    URL_FONTE = "https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados/"
    PASTA = "./dados_brutos"
    extrair_dados_sinesp(URL_FONTE, PASTA)