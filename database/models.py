from sqlalchemy import Column, Integer, String, Date, Float, create_engine
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
from sqlalchemy import text

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

Base = declarative_base()

class OcorrenciaCriminal(Base):
    __tablename__ = 'ocorrencias_criminalidade'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uf = Column(String(2), nullable=False, index=True)
    municipio = Column(String(100), nullable=False, index=True)
    evento = Column(String(100), nullable=False)
    data_referencia = Column(Date, nullable=True)
    agente = Column(String(100), nullable=True)
    arma = Column(String(100), nullable=True)
    faixa_etaria = Column(String(50), nullable=True)
    feminino = Column(Integer, nullable=True)
    masculino = Column(Integer, nullable=True)
    nao_informado = Column(Integer, nullable=True)
    total_vitima = Column(Integer, nullable=True)
    total = Column(Integer, nullable=True)
    total_peso = Column(Float, nullable=True)
    abrangencia = Column(String(50), nullable=True)

def aplicar_indexes(engine, nome_tabela):
    # --- CRIAÇÃO DE ÍNDICES ---
    print("Criando/atualizando índices de busca...")
    
    try:
        with engine.connect() as conn:
            # Índices nas colunas que a IA mais usará para filtrar (WHERE) e agrupar (GROUP BY)
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_uf ON {nome_tabela} (uf);"))
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_municipio ON {nome_tabela} (municipio);"))
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_evento ON {nome_tabela} (evento);"))
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_data ON {nome_tabela} (data_referencia);"))
            conn.commit() # Confirma a criação no banco
            
            print("Índices criados/atualizados com sucesso!\n")
    except Exception as e:
        print(f"Erro durante a criação de índices: {e}\n") 
            
            
# Função para inicializar o banco de dados
def init_db():
    db_url = os.getenv("DATABASE_URL")
    
    
    if not db_url:
        raise ValueError("A variável de ambiente 'DATABASE_URL' não está definida.")
    
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine
