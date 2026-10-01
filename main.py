import json
from sqlalchemy.orm import sessionmaker
from models import init_db, OcorrenciaCriminal
from queries import CriminalidadeService
from datetime import date

# 1. Configuração do Banco
engine = init_db()
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Mock de dados para teste (Simulando registros do banco)
def carregar_dados_teste():
    if session.query(OcorrenciaCriminal).count() == 0:
        dados = [
            # Praia do Canto
            OcorrenciaCriminal(municipio="Vitória", bairro="Praia do Canto", tipo_crime="Roubo de veículo", quantidade=45, data_ocorrencia=date(2025, 5, 10)),
            OcorrenciaCriminal(municipio="Vitória", bairro="Praia do Canto", tipo_crime="Furto de veículo", quantidade=30, data_ocorrencia=date(2025, 6, 12)),
            OcorrenciaCriminal(municipio="Vitória", bairro="Praia do Canto", tipo_crime="Furto a transeunte", quantidade=15, data_ocorrencia=date(2025, 7, 1)),
            
            # Jardim da Penha (Região alternativa com menor incidência)
            OcorrenciaCriminal(municipio="Vitória", bairro="Jardim da Penha", tipo_crime="Roubo de veículo", quantidade=10, data_ocorrencia=date(2025, 5, 11)),
            OcorrenciaCriminal(municipio="Vitória", bairro="Jardim da Penha", tipo_crime="Furto a transeunte", quantidade=8, data_ocorrencia=date(2025, 6, 15)),
        ]
        session.add_all(dados)
        session.commit()

carregar_dados_teste()

# 2. Execução da Consulta (Simulando entrada do usuário: Vitória, Praia do Canto)
service = CriminalidadeService(session)

municipio_alvo = "Vitória"
bairro_alvo = "Praia do Canto"

# Consulta da área informada pelo usuário
dados_destino = service.obter_estatisticas_bairro(municipio_alvo, bairro_alvo)

# Consulta de área alternativa comparativa
dados_alternativa = service.buscar_regiao_alternativa(municipio_alvo, bairro_alvo)

# Estudo do payload consolidado que vai para a LLM / Backend
payload_para_llm = {
    "contexto_destino": dados_destino,
    "sugestao_alternativa": dados_alternativa
}

print("=== PAYLOAD DE DADOS EXTRAÍDOS PARA A LLM ===")
print(json.dumps(payload_para_llm, indent=4, ensure_ascii=False))
