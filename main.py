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
            OcorrenciaCriminal(uf="ES", municipio="Vitória", evento="Feminicídio", feminino=1, total_vitima=1, data_referencia=date(2025, 5, 10)),
            OcorrenciaCriminal(uf="ES", municipio="Vitória", evento="Morte de Agente de Estado", agente="Policial Militar", total_vitima=1, data_referencia=date(2025, 6, 12)),
            OcorrenciaCriminal(uf="ES", municipio="Vitória", evento="Pessoa Desaparecida", faixa_etaria="Menor de Idade", total_vitima=1, data_referencia=date(2025, 7, 1)),
            
            OcorrenciaCriminal(uf="ES", municipio="Vila Velha", evento="Feminicídio", feminino=1, total_vitima=1, data_referencia=date(2025, 5, 11)),
        ]
        session.add_all(dados)
        session.commit()

carregar_dados_teste()

# 2. Execução da Consulta
service = CriminalidadeService(session)

uf_alvo = "ES"
municipio_alvo = "Vitória"

# Consulta da área informada pelo usuário
dados_destino = service.obter_estatisticas_municipio(uf_alvo, municipio_alvo)

# Consulta de área alternativa comparativa
dados_alternativa = service.buscar_municipio_alternativo(uf_alvo, municipio_alvo)

# Estudo do payload consolidado que vai para a LLM / Backend
payload_para_llm = {
    "contexto_destino": dados_destino,
    "sugestao_alternativa": dados_alternativa
}

print("=== PAYLOAD DE DADOS EXTRAÍDOS PARA A LLM ===")
print(json.dumps(payload_para_llm, indent=4, ensure_ascii=False))
