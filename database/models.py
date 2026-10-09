from sqlalchemy import Column, Integer, String, Date, Float, create_engine
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
from sqlalchemy import text

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

Base = declarative_base()

class OcorrenciaCriminal(Base):
    __tablename__ = "ocorrencias_criminalidade"

    id = Column(Integer, primary_key=True, autoincrement=True)

    uf = Column(String(2), nullable=False)
    municipio = Column(String(100), nullable=False)
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
    
    

def aplicar_indexes(engine, nome_tabela="ocorrencias_criminalidade"):
    print("Criando índices de busca...")

    indices = {
        "idx_uf": "uf",
        "idx_municipio": "municipio",
        "idx_evento": "evento",
        "idx_data": "data_referencia",
    }

    try:
        with engine.begin() as conn:
            for nome_indice, coluna in indices.items():
                conn.execute(
                    text(
                        f'CREATE INDEX IF NOT EXISTS "{nome_indice}" '
                        f'ON "{nome_tabela}" ("{coluna}")'
                    )
                )

        print("Índices criados com sucesso!")

    except Exception:
        print("Erro durante a criação dos índices.")
        raise
            
# Função para inicializar o banco de dados
def init_db():
    db_url = os.getenv("DATABASE_URL")
    
    
    if not db_url:
        raise ValueError("A variável de ambiente 'DATABASE_URL' não está definida.")
    
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine
