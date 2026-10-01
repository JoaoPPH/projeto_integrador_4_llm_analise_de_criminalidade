import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import OcorrenciaCriminal

class CriminalidadeService:
    def __init__(self, session: Session):
        self.session = session

    def obter_estatisticas_bairro(self, municipio: str, bairro: str) -> dict:
        """
        Consulta e agrega os totais de crimes por tipo para um determinado bairro/município.
        """
        query = (
            self.session.query(
                OcorrenciaCriminal.tipo_crime,
                func.sum(OcorrenciaCriminal.quantidade).label('total_ocorrencias')
            )
            .filter(
                func.lower(OcorrenciaCriminal.municipio) == municipio.lower(),
                func.lower(OcorrenciaCriminal.bairro) == bairro.lower()
            )
            .group_by(OcorrenciaCriminal.tipo_crime)
            .order_by(func.sum(OcorrenciaCriminal.quantidade).desc())
        )

        df = pd.read_sql(query.statement, self.session.bind)
        
        if df.empty:
            return {
                "municipio": municipio,
                "bairro": bairro,
                "total_geral": 0,
                "detalhes_crimes": {}
            }

        detalhes = df.set_index('tipo_crime')['total_ocorrencias'].to_dict()
        
        return {
            "municipio": municipio,
            "bairro": bairro,
            "total_geral": int(df['total_ocorrencias'].sum()),
            "detalhes_crimes": detalhes
        }

    def buscar_regiao_alternativa(self, municipio: str, bairro_atual: str) -> dict:
        """
        Compara bairros do mesmo município e retorna o bairro com o menor número 
        total de ocorrências para sugerir como alternativa.
        """
        query = (
            self.session.query(
                OcorrenciaCriminal.bairro,
                func.sum(OcorrenciaCriminal.quantidade).label('total_ocorrencias')
            )
            .filter(
                func.lower(OcorrenciaCriminal.municipio) == municipio.lower(),
                func.lower(OcorrenciaCriminal.bairro) != bairro_atual.lower()
            )
            .group_by(OcorrenciaCriminal.bairro)
            .order_by(func.sum(OcorrenciaCriminal.quantidade).asc())
        )

        df = pd.read_sql(query.statement, self.session.bind)

        if df.empty:
            return None

        # Pega o bairro de menor incidência
        melhor_opcao = df.iloc[0]
        
        # Obtém os detalhes de crimes desse bairro alternativo
        detalhes_alt = self.obter_estatisticas_bairro(municipio, melhor_opcao['bairro'])
        
        return detalhes_alt
