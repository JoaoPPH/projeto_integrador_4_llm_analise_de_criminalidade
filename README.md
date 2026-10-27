# Projeto Integrador 4 - LLM - Análise de Criminalidade

Sistema desenvolvido para a disciplina de **Projeto Integrador 4**, no qual os dados de criminalidade pública brasileira são processados através de um pipeline ETL, armazenados em um banco de dados relacional PostgreSQL, disponibilizados em um dashboard interativo no Streamlit e integrados a um **LLM via N8N** para análises e recomendações personalizadas de segurança.

---

## 👥 Grupo
- Estevão Matos de Souza
- Gabriel Ferreira Paulo
- João Pereira Paes Henriques
- Lorena Moreira de Nadai
- Pedro de Oliveira Guimarães
- Thaís Peroni Custodio Lino

**Tema:** Análise de Criminalidade  
**Disciplina:** Projeto Integrador 4  
**Professor Responsável:** Howard Cruz  

---

## 📁 Estrutura de Pastas e Arquivos

```text
projeto_integrador_4_llm_analise_de_criminalidade/
├── database/                  # Módulos de conexão e modelo de banco de dados PostgreSQL
│   ├── main.py                # Script para validação isolada de conexão e payloads
│   ├── models.py              # Configuração SQLAlchemy, criação de tabelas e índices
│   └── queries.py             # Consultas analíticas reutilizáveis em SQL
├── etl/                       # Pipeline de Extração, Transformação e Carga (ETL)
│   ├── carregamento.py        # Carga otimizada via COPY para PostgreSQL
│   ├── extracao_dados.py      # Download dos arquivos fonte (SINESP)
│   ├── orquestrador_etl.py    # Orquestrador do pipeline de dados
│   └── transformacao_dados.py # Tratamento e padronização dos dados brutos
├── services/                  # Serviços de integração externa
│   └── n8n_client.py          # Cliente de comunicação Webhook com o fluxo LLM do N8N
├── views/                     # Módulos das abas de visualização do Streamlit
│   ├── aba_geral.py           # 1. Análises Gerais de Crimes
│   ├── aba_genero.py          # 2. Vítimas por Gênero
│   ├── aba_armas.py           # 3. Armas Apreendidas
│   ├── aba_agentes.py         # 4. Morte de Agentes do Estado
│   ├── aba_drogas.py          # 5. Drogas Apreendidas
│   └── aba_analise_ia.py      # 6. Análise com Inteligência Artificial (LLM)
├── .env                       # Variáveis de ambiente (conexão do banco e URL do N8N)
├── app.py                     # Aplicação principal e entrada do Streamlit
├── requirements.txt           # Dependências e bibliotecas Python do projeto
└── README.md                  # Documentação técnica do projeto
```

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos
- **Python 3.10+** instalado
- **Docker** e **Docker Compose** (opcional, para subir o PostgreSQL em container)

---

### 1. Clonar o Repositório e Instalar Dependências

No terminal da máquina local, execute:

```bash
pip install -r requirements.txt
```

---

### 2. Configurar o Banco de Dados PostgreSQL

#### Opção A: Subir via docker para rodar localmente
Para criar e iniciar uma instância do PostgreSQL via Docker

##### 2.1 Criar o Postgres no docker
```bash
docker run --name postgres-pic4 -e POSTGRES_PASSWORD=suasenha -p 5432:5432 -d postgres:15
```

##### 2.2 Configuração da Variável de Ambiente (`.env`)
Crie um arquivo chamado `.env` na raiz do projeto com a URL de conexão do PostgreSQL:

```env
DATABASE_URL=postgresql://postgres:suasenha@localhost:5432/postgres
```

##### 2.3 Executar o Pipeline ETL
Para baixar, tratar e carregar a base de dados histórica para o banco de dados PostgreSQL, execute:

```bash
python -m etl.orquestrador_etl
```

> **Nota:** O script criará a tabela `ocorrencias_criminalidade`, baixará as bases e criará os índices de busca otimizados no PostgreSQL.

#### Opção B: Configuração da Variável de Ambiente (`.env`) para rodar com a nuvem
Crie um arquivo chamado `.env` na raiz do projeto com a URL de conexão do PostgreSQL:

```env
PASTA_DADOS=./dados_brutos
DATABASE_URL=postgresql://neondb_owner:npg_9OVhEkPKmL0i@ep-sweet-waterfall-b5c88b0h-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

---

### 3. Iniciar o Dashboard Interativo (Streamlit)

Após o término da execução do ETL, inicie o aplicativo web:

```bash
streamlit run app.py
```

O dashboard abrirá automaticamente no navegador no endereço `http://localhost:8501`.

---

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3.10+
- **Interface Web:** Streamlit
- **Integração LLM / IA:** N8N Webhook & Agentic Workflow
- **Visualização de Dados:** Plotly Express / Plotly Graph Objects
- **Banco de Dados:** PostgreSQL & SQLAlchemy
- **Machine Learning & Regressão:** Scikit-Learn, XGBoost, Random Forest
- **Processamento de Dados:** Pandas & NumPy