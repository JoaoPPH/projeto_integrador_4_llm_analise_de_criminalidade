from sqlalchemy import Column, Integer, String, Date, Float, create_engine
from sqlalchemy.orm import declarative_base

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

# Função para inicializar o banco de dados
def init_db(db_url="sqlite:///criminalidade.db"):
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine
