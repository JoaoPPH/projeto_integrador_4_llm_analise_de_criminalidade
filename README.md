# Projeto Integrador 4 - LLM - Análise de Criminalidade

Sistema desenvolvido para a disciplina de **Projeto Integrador 4**, no qual os dados de criminalidade pública brasileira são processados através de um pipeline ETL, armazenados em um banco de dados relacional PostgreSQL e disponibilizados em um dashboard interativo no Streamlit.

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
├── database/            # Módulos de conexão e modelo de banco de dados PostgreSQL
│   ├── main.py          # Script para validação isolada de conexão e payloads
│   ├── models.py        # Configuração SQLAlchemy, criação de tabelas e índices
│   └── queries.py       # Consultas analíticas reutilizáveis em SQL
├── etl/                 # Pipeline de Extração, Transformação e Carga (ETL)
│   ├── carregamento.py       # Carga otimizada via COPY para PostgreSQL
│   ├── extracao_dados.py    # Download dos arquivos fonte (SINESP)
│   ├── orquestrador_etl.py  # Orquestrador do pipeline de dados
│   └── transformacao_dados.py# Tratamento e padronização dos dados brutos
├── views/               # Módulos das abas de visualização do Streamlit
│   ├── aba_geral.py     # 1. Análises Gerais de Crimes
│   ├── aba_genero.py    # 2. Vítimas por Gênero
│   ├── aba_armas.py     # 3. Armas Apreendidas
│   ├── aba_agentes.py   # 4. Morte de Agentes do Estado
│   └── aba_drogas.py    # 5. Drogas Apreendidas
├── .env                 # Variáveis de ambiente (string de conexão do banco)
├── app.py               # Aplicação principal e entrada do Streamlit
├── requirements.txt     # Dependências e bibliotecas Python do projeto
└── README.md            # Documentação técnica do projeto
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
# Instalar todas as dependências do projeto
pip install -r requirements.txt
```

---

### 2. Configurar o Banco de Dados PostgreSQL

#### Opção A: Subir via Docker (Recomendado)
Para criar e iniciar uma instância do PostgreSQL via Docker:

```bash
docker run --name postgres-pic4 -e POSTGRES_PASSWORD=suasenha -p 5432:5432 -d postgres:15
```

#### Opção B: Configuração da Variável de Ambiente (`.env`)
Crie um arquivo chamado `.env` na raiz do projeto com a URL de conexão do PostgreSQL:

```env
DATABASE_URL=postgresql://postgres:suasenha@localhost:5432/postgres
```

---

### 3. Executar o Pipeline ETL

Para baixar, tratar e carregar a base de dados histórica para o banco de dados PostgreSQL, execute:

```bash
python -m etl.orquestrador_etl
```

> **Nota:** O script criará a tabela `ocorrencias_criminalidade`, baixará as bases e criará os índices de busca otimizados no PostgreSQL.

---

### 4. Iniciar o Dashboard Interativo (Streamlit)

Após o término da execução do ETL, inicie o aplicativo web:

```bash
streamlit run app.py
```

O dashboard abrirá automaticamente no navegador no endereço `http://localhost:8501`.

---

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3.10+
- **Interface Web:** Streamlit
- **Visualização de Dados:** Plotly Express / Plotly Graph Objects
- **Banco de Dados:** PostgreSQL & SQLAlchemy
- **Machine Learning & Regressão:** Scikit-Learn, XGBoost, Random Forest
- **Processamento de Dados:** Pandas & NumPy