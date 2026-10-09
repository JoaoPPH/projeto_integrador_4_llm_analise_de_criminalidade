# arquivo: transform.py
import pandas as pd
import os
import time

def transformar_dados_sinesp(caminho_arquivo):
    """
    Lê o arquivo, agrupa duplicidades para 'Tentativa de Homicídio' e 'Estupro' 
    (somando as vítimas) e retorna o DataFrame tratado.
    """
    nome_arquivo = os.path.basename(caminho_arquivo)
    print(f"\nIniciando transformação: {nome_arquivo}...")
    
    try:
        
        inicio = time.perf_counter()
        # 1. Leitura do arquivo
        if caminho_arquivo.endswith('.xlsx'):
            print("Lendo arquivo Excel (xlsx)...")
            df = pd.read_excel(caminho_arquivo)
        else:
            print("Lendo arquivo CSV...")
            df = pd.read_csv(
                caminho_arquivo,
                sep=';',
                encoding='utf-8',
                engine='pyarrow',
                decimal=','
            )
            
        fim_leitura = time.perf_counter()
        
        print(
            f"Leitura concluída: "
            f"{fim_leitura - inicio:.2f}s"
        )
            
        # 2. Definição das colunas (conforme o padrão validado no arquivo de 2023)
        colunas_chave = ['uf', 'municipio', 'evento', 'data_referencia']
        colunas_valores = ['feminino', 'masculino', 'nao_informado', 'total_vitima', 'total', 'total_peso']
        
        # Garante que só tentará somar colunas que realmente existem no arquivo atual
        colunas_valores_presentes = [col for col in colunas_valores if col in df.columns]
        
        
        # --- TRATAMENTO DE NULOS ---
        # Substitui NaN numéricos por 0
        df[colunas_valores_presentes] = df[colunas_valores_presentes].fillna(0)
                
        # Substitui NaN de texto por "Não Informado"
        colunas_texto = [c for c in df.columns if c not in colunas_valores_presentes]
        df[colunas_texto] = df[colunas_texto].fillna("Não Informado")
        # ---------------------------------
        
        #------ TRATAMENTO PARA O FLOAT -----------
        if "total_peso" in df.columns:
            df["total_peso"] = pd.to_numeric(
                df["total_peso"],
                errors="raise"
            )
            
        print("Tipo de total_peso:", df["total_peso"].dtype)
        print("Valores não zero:", (df["total_peso"] != 0).sum())
        print("Valores nulos:", df["total_peso"].isna().sum())
        print("Maiores valores:")
        print(df["total_peso"].nlargest(10))
        
        # 3. Separação dos dados
        mascara_crimes = df['evento'].isin(['Tentativa de Homicídio', 'Estupro'])
        df_agrupar = df[mascara_crimes]
        df_manter = df[~mascara_crimes]
        
        if not df_agrupar.empty:
            # 4. Aplicação das regras de agregação (soma para números, mantém o 1º valor para textos)
            regras_agg = {col: 'sum' for col in colunas_valores_presentes}
            
            colunas_texto = [c for c in df.columns if c not in colunas_chave + colunas_valores_presentes]
            for col in colunas_texto:
                regras_agg[col] = 'first'
                
            df_agrupado = df_agrupar.groupby(colunas_chave, as_index=False).agg(regras_agg)
            
            # 5. União dos dados tratados com os crimes que não precisavam de soma
            df_final = pd.concat([df_manter, df_agrupado], ignore_index=True)
            print(f"Transformação concluída: {len(df)} linhas originais -> {len(df_final)} linhas finais.")
        else:
            df_final = df
            print("Nenhum registro de Tentativa de Homicídio ou Estupro que exija agrupamento.")
            
            
        fim_transformacao = time.perf_counter()

        print(
            f"Transformação concluída: "
            f"{fim_transformacao - fim_leitura:.2f}s"
        )

        print(
            f"Total transformação: "
            f"{fim_transformacao - inicio:.2f}s"
        )
        
        return df_final
        
    except Exception as e:
        print(f"Erro ao transformar {nome_arquivo}: {e}")
        return None

# Se quiser testar o arquivo isoladamente:
if __name__ == "__main__":
    # Teste apontando para o arquivo de 2023 que você baixou
    ARQUIVO_TESTE = "./dados_brutos/BancoVDE 2015.csv" 
    if os.path.exists(ARQUIVO_TESTE):
        df_resultado = transformar_dados_sinesp(ARQUIVO_TESTE)
        if df_resultado is not None:
            print(df_resultado.head(3))
    else:
        print(f"Arquivo não encontrado para teste em {ARQUIVO_TESTE}")