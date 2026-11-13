# Rota Segura

Consulta de segurança por destino, com Inteligência Artificial, sobre a base
pública de ocorrências de criminalidade do Brasil.

Projeto Integrador 4 — Análise de Criminalidade.

Aplicação em **processo único Python**: o FastAPI serve tanto a API quanto a
interface web. Em runtime não há build nem dependência de Node.

Este README cobre o **runtime Python** (API + UI publicada). O frontend de
desenvolvimento tem README próprio em
[`../frontend-next/README.md`](../frontend-next/README.md).

As alterações de interface são feitas no frontend Next na pasta irmã
`../frontend-next/` e publicadas como export estático em `ui/`.
O fluxo completo está em
[Alterações da UI](#alterações-da-ui-next--ui-automático).

---

## Funcionalidades

### Consulta IA — `/`

1. Seleção de estado e município (combobox pesquisável).
2. Contexto da viagem: transporte, acompanhantes, período e objetivo
   (com opção de descrição livre).
3. Opção de aceitar uma cidade alternativa mais tranquila no mesmo estado.
4. Resultado em duas colunas:
   - narrativa de segurança gerada pela IA;
   - perfil real do destino (total de ocorrências, tipos mais frequentes,
     barras comparativas) e cartão da alternativa.

### Panorama nacional — `/panorama`

Agregações da base inteira: ocorrências por estado, evolução anual, vítimas por
gênero, armas apreendidas, mortes de agentes do Estado e drogas apreendidas
(toneladas por ano).

---

## Stack

| Camada        | Tecnologia                                              |
| ------------- | ------------------------------------------------------- |
| Interface     | export estático do Next em `ui`                       |
| API           | Python 3.11+, FastAPI, Uvicorn, Pydantic                |
| Banco         | PostgreSQL (Neon) via psycopg 3 com pool de conexões    |
| IA            | Groq — API compatível com OpenAI (`openai/gpt-oss-120b`) |
| Configuração  | python-dotenv (`.env`)                                  |

---

## Arquitetura

```
Navegador
   │
   ▼
FastAPI (um processo, porta 8000)
   ├── UI estática        ui/** (export do Next)
   ├── API REST           /api/**
   ├── PostgreSQL         Neon (ocorrencias_criminalidade)
   └── IA                 Groq (com fallback local pelos dados)
```

- A UI conversa apenas com a própria origem (`/api/*`).
- A UI de `ui/` é o export estático de `../frontend-next/`.
- O Markdown devolvido pela IA é escapado e renderizado no servidor antes de
  chegar ao navegador (`app/markdown_render.py`).
- Sem credencial ou com a IA indisponível, a API monta um briefing a partir das
  estatísticas reais, rotulado como **análise automática (dados oficiais)**.

---

## Estrutura do projeto

```
PI4C3/
├── frontend-next/              origem das alterações de UI (Next.js)
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── .gitignore
│   └── package.json
└── final-project/
    ├── run.py                  inicia a aplicação (uvicorn)
    ├── .env.example            modelo de configuração
    ├── scripts/
    │   └── exportar_ui.py      build do Next + publicação em ui/
    ├── ui/                     export estático gerado (não editar)
    └── app/                    pacote Python (API)
        ├── main.py             app FastAPI, rotas /api e mount da UI
        ├── config.py           variáveis de ambiente e defaults
        ├── db.py               pool psycopg e filtros SQL
        ├── catalogo.py         UFs e municípios (cache)
        ├── estatisticas.py     agregados por município + alternativa
        ├── perfil.py           período, gênero e evolução anual
        ├── categorias.py       agrupamento de eventos em categorias
        ├── panorama.py         agregações nacionais (cache)
        ├── llm.py              cliente Groq + montagem do prompt
        ├── briefing.py         fallback fundamentado nos dados
        ├── contexto.py         compromisso fixo x destino flexível
        ├── markdown_render.py  Markdown seguro para HTML
        ├── cache.py            cache TTL com single-flight
        └── requirements.txt
```

---

## Alterações da UI (Next → `/ui`, automático)

A UI publicada é o **export estático do Next**. Não há conversão manual: o
Next gera o HTML/CSS/JS e o FastAPI serve o resultado.

### 1. Rodar a aplicação

```powershell
python run.py
```

### 2. Desenvolver no Next

```powershell
cd ..\frontend-next
npm install          # só na primeira vez
npm run dev -- -p 3100
```

Abra http://localhost:3100. O `next.config.ts` encaminha `/api/*` para
`http://127.0.0.1:8000` (padrão). Para outra API, crie
`../frontend-next/.env.local` com `API_URL=http://127.0.0.1:8000`.

### 3. Publicar em `ui`

```powershell
python scripts/exportar_ui.py
```

O script roda `next build` com `NEXT_EXPORT=1` (ativa `output: "export"` e
`trailingSlash`) na pasta irmã `../frontend-next` e copia `out` para
`ui`.

### 4. Validar a versão publicada

Recarregue http://127.0.0.1:8000 e refaça o fluxo alterado. O log do uvicorn
mostra os acessos aos arquivos `/_next/...`.

Observações:

- No modo export os `rewrites` não são usados: como a UI é servida pelo FastAPI
  na mesma origem, as chamadas relativas `/api/*` caem direto na API.
- Tudo em `ui/` é gerado; não edite esses arquivos à mão.
- Node é necessário somente para desenvolver/publicar a UI; o runtime é Python.
- `/panorama` redireciona para `/panorama/` por causa do `trailingSlash`.

### Checklist

- [ ] Mudança implementada e validada no Next (porta 3100).
- [ ] `python scripts/exportar_ui.py` executado sem erro.
- [ ] `/` e `/panorama/` abrindo em http://127.0.0.1:8000 com os assets `_next`.
- [ ] Nenhuma mudança no contrato da API.

---

## Requisitos

- Python 3.11 ou superior
- Node.js 20+ e npm (somente para alterar a UI via `../frontend-next/`)
- Acesso à rede para o PostgreSQL (Neon) e para a Groq
- Navegador moderno

---

## Instalação

```powershell
cd C:\Users\Administrator\Desktop\PI4C3\final-project

python -m venv .venv
.venv\Scripts\activate
python -m pip install -r app\requirements.txt

copy .env.example .env
```

Em Linux/macOS:

```bash
cd final-project
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r app/requirements.txt
cp .env.example .env
```

Preencha o `.env` com a `DATABASE_URL` e a `LLM_API_KEY`. Nesta máquina o `.env`
já está configurado.

---

## Execução

```powershell
python run.py
```

- Aplicação: **http://127.0.0.1:8000**
- Documentação interativa: **http://127.0.0.1:8000/docs**
- Status: **http://127.0.0.1:8000/api/health**

Variáveis opcionais do `run.py`:

| Variável | Padrão      | Descrição                                  |
| -------- | ----------- | ------------------------------------------ |
| `HOST`   | `127.0.0.1` | Interface de escuta                        |
| `PORT`   | `8000`      | Porta                                      |
| `RELOAD` | `1`         | Recarrega ao salvar; use `0` em produção   |

Exemplo em produção:

```powershell
$env:RELOAD="0"; python run.py
```

---

## Configuração (`.env`)

| Variável        | Descrição                                                    |
| --------------- | ------------------------------------------------------------ |
| `DATABASE_URL`  | Conexão PostgreSQL (mesma base alimentada pelo ETL).         |
| `LLM_API_KEY`   | Chave da Groq (há um padrão em `app/config.py`).   |
| `LLM_BASE_URL`  | Base da API da Groq (compatível com OpenAI).                 |
| `LLM_MODEL`     | Modelo usado (padrão: `openai/gpt-oss-120b`).                |
| `LLM_TIMEOUT_S` | Tempo máximo de espera da IA, em segundos (padrão: 75).      |

O `.env` é ignorado pelo git. Não versione credenciais.

---

## API

| Método | Rota                                                       | Descrição                                    |
| ------ | ---------------------------------------------------------- | -------------------------------------------- |
| GET    | `/api/ufs`                                                 | Estados disponíveis                          |
| GET    | `/api/municipios?uf=XX`                                    | Municípios de um estado                      |
| GET    | `/api/estatisticas?uf=XX&municipio=Nome`                   | Perfil do destino + alternativa              |
| POST   | `/api/analise`                                             | Análise da IA com fallback pelos dados       |
| GET    | `/api/panorama`                                            | Agregações nacionais                         |
| GET    | `/api/health`                                              | Status da API e da IA                        |

### Exemplos

**Municípios**

```http
GET /api/municipios?uf=ES
```

```json
{ "municipios": ["AFONSO CLAUDIO", "ALEGRE", "..."] }
```

**Estatísticas**

```http
GET /api/estatisticas?uf=ES&municipio=Vitória
```

```json
{
  "destino": {
    "uf": "ES",
    "municipio": "Vitória",
    "total_geral": 5079,
    "detalhes_eventos": { "Mandado de prisão cumprido": 3217, "Tentativa de homicídio": 825 }
  },
  "alternativa": {
    "uf": "ES",
    "municipio": "APIACÁ",
    "total_geral": 70
  }
}
```

**Análise**

```http
POST /api/analise
Content-Type: application/json
```

```json
{
  "uf": "ES",
  "municipio": "Vitória",
  "meio_transporte": "Transporte público",
  "acompanhantes": "Família",
  "periodo": "Noite",
  "objetivo": "Turismo",
  "aceita_alternativa": true
}
```

Resposta (sucesso):

```json
{
  "success": true,
  "analise": "### Resumo executivo\n...",
  "analise_html": "<h3>Resumo executivo</h3>...",
  "modelo": "openai/gpt-oss-120b",
  "tokens_utilizados": 1634,
  "dados": { "destino": {}, "alternativa": {}, "contexto_usuario": {} },
  "fonte": "ia"
}
```

Em falha da IA, `fonte` é `"fallback"`, `modelo` é
`"Análise automática (dados oficiais)"` e há o campo `aviso`.

Erros usam `{ "error": "mensagem" }` com status 400, 500 ou 502.

---

## Modelo de dados

Tabela `ocorrencias_criminalidade` (Neon):

| Coluna             | Tipo      | Uso                                          |
| ------------------ | --------- | -------------------------------------------- |
| `id`               | inteiro   | Chave primária                               |
| `uf`               | texto     | Sigla do estado (indexado)                   |
| `municipio`        | texto     | Nome do município (indexado)                 |
| `evento`           | texto     | Tipo de ocorrência (indexado)                |
| `data_referencia`  | data      | Data do registro (indexado)                  |
| `agente`           | texto     | Tipo de agente do Estado                     |
| `arma`             | texto     | Tipo de arma                                 |
| `faixa_etaria`     | texto     | Faixa etária                                 |
| `feminino`, `masculino`, `nao_informado` | inteiro | Vítimas por gênero |
| `total_vitima`     | inteiro   | Total de vítimas                            |
| `total`            | inteiro   | Total de ocorrências                        |
| `total_peso`       | decimal   | Peso de drogas apreendidas                   |
| `abrangencia`      | texto     | Abrangência do registro                      |

Índices existentes: `idx_uf`, `idx_municipio`, `idx_evento`, `idx_data`.

---

## IA e fallback

- O prompt recebe: total do destino, eventos mais frequentes com participação
  percentual, comparação com a alternativa (quando aplicável) e o contexto do
  usuário.
- Para compromissos com horário/local fixo (show, evento, jogo, reunião), a IA
  **não sugere trocar de cidade**: foca em chegada, permanência e saída,
  transporte, estacionamento e segurança pessoal.
- A alternativa só é sugerida quando o usuário marca a opção **e** o destino é
  flexível.
- A resposta é estruturada em seções: resumo executivo, riscos e recomendações;
  a seção de alternativa é incluída apenas nos casos acima.
- Se a Groq falhar, expirar ou faltar credencial, o `briefing.py` gera uma
  leitura em Markdown a partir dos dados oficiais. A UI indica a origem.

---

## Desempenho e cache

| Dado          | TTL padrão | Variável de ambiente      |
| ------------- | ---------- | ------------------------- |
| UFs/municípios | 1 hora    | `CACHE_CATALOGO_S`        |
| Estatísticas  | 15 minutos | `CACHE_ESTATISTICAS_S`    |
| Análises      | 10 minutos | `CACHE_ANALISE_S`         |
| Panorama      | 1 hora     | `CACHE_PANORAMA_S`        |

- Pool de conexões reaproveitado (máximo de 8).
- Consultas usam igualdade nas colunas indexadas e faixa de datas sem função na
  coluna.
- O panorama roda em paralelo com limite de 3 consultas simultâneas.
- Os caches são por processo; múltiplos workers teriam caches independentes.

---

## Segurança

- Credenciais apenas no `.env` (ignorado pelo git).
- Todo texto vindo do usuário é limitado por tamanho na borda (Pydantic).
- Consultas SQL usam parâmetros, sem interpolação de valores.
- O Markdown da IA é escapado antes da renderização; a UI injeta apenas o HTML
  já sanitizado no servidor.

---

## Solução de problemas

| Sintoma                              | Causa provável / solução                                  |
| ------------------------------------ | --------------------------------------------------------- |
| `ModuleNotFoundError`                | instale as dependências: `pip install -r app/requirements.txt` |
| Erro de conexão com o banco          | confira `DATABASE_URL` e a rede                            |
| `ia_configurada: false`              | falta `LLM_API_KEY` ou ela é inválida                      |
| Resposta com `fonte: "fallback"`     | Groq indisponível, limite atingido ou chave inválida       |
| Porta 8000 ocupada                   | `$env:PORT="8010"; python run.py`                          |
| Fontes com aparência diferente       | sem acesso ao Google Fonts; o CSS usa fontes de sistema como fallback |
| Panorama lento na primeira abertura  | agrega 4,4 milhões de linhas; depois fica em cache por 1h  |

---

## Frontend de desenvolvimento (Next)

`../frontend-next/` é a origem das alterações de interface. Ele não roda em
produção; a versão publicada é o export em `ui/`. Consulte o
[README do frontend](../frontend-next/README.md) e o fluxo em
[Alterações da UI](#alterações-da-ui-next--ui-automático).

---

## Aviso

As recomendações são orientativas, derivam de dados históricos e não substituem
o bom senso nem as orientações das autoridades de segurança locais.
