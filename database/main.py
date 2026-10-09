import json
from sqlalchemy.orm import sessionmaker
from models import init_db, OcorrenciaCriminal
from queries import CriminalidadeService
from datetime import date


# 1. Configuração do Banco
engine = init_db()
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
nome_tabela = OcorrenciaCriminal.__tablename__  # Obtém o nome da tabela a partir do modelo

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
