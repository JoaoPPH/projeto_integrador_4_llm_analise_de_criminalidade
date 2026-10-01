from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class OcorrenciaCriminal(Base):
    __tablename__ = 'ocorrencias_criminalidade'

    id = Column(Integer, primary_key=True, autoincrement=True)
    municipio = Column(String(100), nullable=False, index=True)
    bairro = Column(String(100), nullable=False, index=True)
    tipo_crime = Column(String(100), nullable=False)  # Ex: Roubo de veículo, Furto, etc.
    data_ocorrencia = Column(Date, nullable=False)
    quantidade = Column(Integer, default=1)

# Função para inicializar o banco de dados
def init_db(db_url="sqlite:///criminalidade_es.db"):
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return engine
