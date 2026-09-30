# arquivo: load.py
from sqlalchemy import create_engine, text

def carregar_dados_sinesp(df, nome_tabela, string_conexao):
    if df is None or df.empty:
        print("Nenhum dado para inserir.")
        return False
        
    print(f"Carregando {len(df)} registros na tabela '{nome_tabela}'...")
    try:
        engine = create_engine(string_conexao)
        
        # Insere os dados
        df.to_sql(name=nome_tabela, con=engine, if_exists='append', index=False)
        
        # --- CRIAÇÃO DE ÍNDICES ---
        print("Criando/atualizando índices de busca...")
        with engine.connect() as conn:
            # Índices nas colunas que a IA mais usará para filtrar (WHERE) e agrupar (GROUP BY)
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_uf ON {nome_tabela} (uf);"))
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_municipio ON {nome_tabela} (municipio);"))
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_evento ON {nome_tabela} (evento);"))
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_data ON {nome_tabela} (data_referencia);"))
            conn.commit() # Confirma a criação no banco
        # --------------------------
        
        print("Carga e indexação concluídas com sucesso!\n")
        return True
        
    except Exception as e:
        print(f"Erro durante a carga: {e}\n")
        return False