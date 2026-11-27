# Análise de Impacto Social, IA Responsável e Governança — Rota Segura

**Projeto:** Rota Segura — Análise de Criminalidade e Recomendações de Segurança com IA  

**Grupo**:
- Estevão Matos de Souza;
- Gabriel Ferreira Paulo;
- João Pereira Paes Henriques;
- Lorena Moreira de Nadai;
- Pedro de Oliveira Guimarães;
- Thaís Peroni Custodio Lino.

**Disciplina:** Projeto Integrador IV (2026/2) — FAESA  
**Professor Responsável:** Howard Cruz Roatti  
**Área Temática:** Direitos Humanos e Justiça / Cidades Inteligentes e Segurança Pública

Este documento dá continuidade ao escopo, à caracterização da comunidade e aos indicadores propostos no **Relatório da C1 (setembro de 2026)**, consolidando-os na versão MVP da C3 (**Rota Segura**).

---

## 1. Natureza Extensionista e Comunidade Impactada

### 1.1 Identificação e Caracterização da Comunidade
O **Rota Segura** foi desenvolvido para atender cidadãos em deslocamento urbano ou intermunicipal — incluindo viajantes, turistas, moradores, estudantes, famílias e profissionais em mobilidade — que precisam planejar rotas, horários e deslocamentos com base em evidências reais de segurança pública, com recorte nacional baseado no **SINESP (Sistema Nacional de Informações de Segurança Pública)** e aplicações práticas em estados como o **Espírito Santo**.

Na continuidade do **Relatório da C1**, o público-alvo abrange:
- **Cidadãos, moradores e viajantes:** Pessoas que utilizam as informações e recomendações contextualizadas para tomar decisões mais seguras em trajetos, viagens e rotinas, evitando exposições desnecessárias em cenários de maior risco.
- **Gestores de segurança pública e ONGs:** Órgãos e iniciativas que podem observar indicadores agregados por localidade e tipologia para apoiar análises regionais e ações preventivas.

### 1.2 Problema Concreto Resolvido
Embora os dados oficiais de segurança pública sejam abertos, na prática eles ficam distribuídos em planilhas extensas com milhões de registros e categorias técnicas de difícil interpretação para o usuário comum.

O **Rota Segura** endereça esse problema ao:
- **Reduzir a assimetria de informação:** Traduz dados históricos agregados em orientações contextualizadas de acordo com o destino, meio de transporte, acompanhantes, período e objetivo da viagem.
- **Evitar leituras superficiais ou distorcidas:** Diferencia o perfil das ocorrências e oferece, quando aplicável e aceito pelo usuário, alternativas de municípios com menor incidência dentro do mesmo estado.

---

## 2. Indicadores de Impacto e Métricas de Avaliação

A partir das diretrizes de impacto definidas na **C1** e da arquitetura implementada no **MVP da C3**, o impacto da solução é acompanhado pelos seguintes indicadores:

| Dimensão | Indicador | Meta / Comportamento Esperado | Forma de Medição |
| :--- | :--- | :--- | :--- |
| **Cobertura de Dados** | Volume de registros históricos estruturados e consultáveis | Base consolidada (~4,4 milhões de linhas no modelo de dados) acessível por UF, município e panorama | Contagem de registros na tabela `ocorrencias_criminalidade` e endpoints `/api/estatisticas` e `/api/panorama` |
| **Desempenho e Acesso** | Tempo de resposta das consultas e análises | Resposta ágil apoiada por cache em memória com TTL e pool de conexões | Verificação de latência nos endpoints da API e logs de execução |
| **Qualidade da IA (Eval)** | Relevância, aderência ao contexto e fidelidade aos dados | Avaliações cobrindo critérios de contexto (transporte, acompanhantes, período, objetivo) e fidelidade às estatísticas | Execução de testes de avaliação (`evals/avaliacao_ia.py`) e análise dos resultados |
| **Resiliência do Serviço** | Continuidade da resposta mesmo sem disponibilidade do LLM | Geração de análise estruturada via *fallback* determinístico baseado nos dados oficiais | Comportamento do módulo `briefing.py` quando a IA está indisponível ou sem credencial |
| **Acessibilidade** | Disponibilidade pública sem barreira técnica | Acesso web gratuito sem necessidade de cadastro ou manipulação de planilhas brutas | Deploy público na nuvem e navegação pelas rotas `/` e `/panorama` |

---

## 3. IA Responsável e Governança

Em conformidade com os requisitos de **IA Responsável e Governança** do edital, o sistema incorpora medidas técnicas e operacionais para mitigar riscos:

### 3.1 Privacidade e LGPD
- **Dados públicos e agregados:** As estatísticas de criminalidade utilizadas são dados públicos agregados, sem identificação individual de cidadãos (sem nomes, documentos ou dados pessoais sensíveis).
- **Minimização de dados na consulta:** A aplicação não exige login nem coleta rastreamento contínuo de localização. Os parâmetros informados na consulta são usados para gerar a análise solicitada sem associá-los a identificação pessoal.

### 3.2 Segurança e Mitigação de Riscos
- **Validação e sanitização:** As entradas da API passam por validação (como limites de tamanho via Pydantic) e consultas SQL parametrizadas, reduzindo riscos de entrada malformada ou injeção. O conteúdo Markdown retornado pela IA é tratado no servidor (`markdown_render.py`) antes de ser exibido na interface.
- **Gestão de segredos e *fallback*:** Chaves de API e credenciais de banco ficam isoladas em variáveis de ambiente (`.env`), fora do versionamento. Em caso de falha, ausência de chave ou indisponibilidade do modelo remoto, o sistema recorre ao *fallback* local (`briefing.py`), mantendo uma resposta fundamentada nos dados oficiais com identificação clara da origem.

### 3.3 Ética, Viés e Transparência
- **Cuidado contra vieses e estigmatização:** Registros oficiais refletem tanto ocorrências quanto dinâmicas de registro e atuação policial (como cumprimento de mandados frente a crimes violentos contra a pessoa). O sistema busca contextualizar os números e evitar conclusões absolutas ou estigmatização indevida de cidades.
- **Respeito a compromissos fixos:** Quando o objetivo envolve local ou horário fixo (como evento, show, jogo ou compromisso pontual), a sugestão de troca de município não é forçada, focando em orientações práticas de chegada, permanência e saída.
- **Caráter orientativo:** A aplicação informa que as recomendações têm caráter orientativo, baseiam-se em dados históricos e não substituem o bom senso nem as orientações oficiais das autoridades de segurança.

### 3.4 Custo e Sustentabilidade
- **Operação de baixo custo:** O uso de API de LLM em camada gratuita (Groq) e o apoio a mecanismos de *fallback* local permitem operar o componente de IA sem custos financeiros elevados para o projeto.
- **Eficiência computacional:** O uso de cache com TTL (para catálogos, estatísticas, análises e panorama) e reaproveitamento de conexões reduz consultas repetidas ao banco e chamadas desnecessárias ao modelo, diminuindo tempo de espera e consumo de recursos.

---

## 4. Registro de Uso de IA no Desenvolvimento (Integridade Acadêmica)

Conforme a diretriz de integridade acadêmica do edital, o uso de ferramentas de IA generativa durante o desenvolvimento do projeto ocorreu como apoio técnico, com revisão e validação da equipe:

- **Arquitetura, dados e consultas:** Apoio na estruturação de consultas, organização de módulos e revisão técnica da integração com o banco PostgreSQL e endpoints da API.
- **Engenharia de prompt e renderização:** Apoio na definição da estrutura das respostas e na sanitização segura do Markdown para exibição na interface.
- **Testes, avaliação e documentação:** Apoio na escrita de testes unitários, roteiros de avaliação manual da IA e redação/organização da documentação técnica do repositório.