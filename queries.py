import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import OcorrenciaCriminal

class CriminalidadeService:
    def __init__(self, session: Session):
        self.session = session

    def obter_estatisticas_municipio(self, uf: str, municipio: str) -> dict:
        """
        Consulta e agrega os totais de ocorrências por evento para um determinado município/uf.
        """
        query = (
            self.session.query(
                OcorrenciaCriminal.evento,
                func.count(OcorrenciaCriminal.id).label('total_ocorrencias')
            )
            .filter(
                func.lower(OcorrenciaCriminal.uf) == uf.lower(),
                func.lower(OcorrenciaCriminal.municipio) == municipio.lower()
            )
            .group_by(OcorrenciaCriminal.evento)
            .order_by(func.count(OcorrenciaCriminal.id).desc())
        )

        df = pd.read_sql(query.statement, self.session.bind)
        
        if df.empty:
            return {
                "uf": uf,
                "municipio": municipio,
                "total_geral": 0,
                "detalhes_eventos": {}
            }

        detalhes = df.set_index('evento')['total_ocorrencias'].to_dict()
        
        return {
            "uf": uf,
            "municipio": municipio,
            "total_geral": int(df['total_ocorrencias'].sum()),
            "detalhes_eventos": detalhes
        }

    def buscar_municipio_alternativo(self, uf: str, municipio_atual: str) -> dict:
        """
        Compara municípios do mesmo estado e retorna o município com o menor número 
        total de ocorrências para sugerir como alternativa.
        """
        query = (
            self.session.query(
                OcorrenciaCriminal.municipio,
                func.count(OcorrenciaCriminal.id).label('total_ocorrencias')
            )
            .filter(
                func.lower(OcorrenciaCriminal.uf) == uf.lower(),
                func.lower(OcorrenciaCriminal.municipio) != municipio_atual.lower()
            )
            .group_by(OcorrenciaCriminal.municipio)
            .order_by(func.count(OcorrenciaCriminal.id).asc())
        )

        df = pd.read_sql(query.statement, self.session.bind)

        if df.empty:
            return None

        # Pega o município de menor incidência
        melhor_opcao = df.iloc[0]
        
        # Obtém os detalhes de eventos desse município alternativo
        detalhes_alt = self.obter_estatisticas_municipio(uf, melhor_opcao['municipio'])
        
        return detalhes_alt
