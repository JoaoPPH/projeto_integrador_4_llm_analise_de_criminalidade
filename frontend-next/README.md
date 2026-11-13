# Rota Segura — Frontend (Next.js)

Interface de desenvolvimento do projeto. Este app não roda em produção: a
versão publicada é o export estático em `../final-project/ui`, servido pelo
FastAPI.

## Páginas

- `/` — consulta de segurança por destino (estado, município, contexto da
  viagem e análise da IA).
- `/panorama` — ocorrências por estado, evolução anual, gênero, armas, agentes
  e drogas.

## Stack

- Next.js 16 (App Router), React 19 e TypeScript
- Tailwind CSS 4
- Recharts, react-markdown, remark-gfm e lucide-react

## Estrutura

```
frontend-next/
├── app/
│   ├── layout.tsx              layout e fontes
│   ├── page.tsx                consulta
│   ├── panorama/page.tsx       panorama
│   └── globals.css             tema
├── components/
│   ├── ConsultaIA.tsx, Combobox.tsx, PainelDestino.tsx, Narrativa.tsx
│   ├── charts/                 gráficos Recharts
│   └── panorama/Panorama.tsx
├── lib/                        tipos, formatação e UFs
├── next.config.ts              rewrites /api e modo export
└── package.json
```

## Requisitos

- Node.js 20+ e npm
- API Python rodando em `http://127.0.0.1:8000`

## Desenvolvimento

Em um terminal, suba a API:

```powershell
cd ..\final-project
python run.py
```

Em outro, suba o Next:

```powershell
cd C:\Users\Administrator\Desktop\PI4C3\frontend-next
npm install          # só na primeira vez
npm run dev -- -p 3100
```

Abra http://localhost:3100.

O `next.config.ts` encaminha `/api/*` para `http://127.0.0.1:8000`. Para outra
API, crie `.env.local`:

```
API_URL=http://127.0.0.1:8000
```

A porta 3000 pode estar ocupada por outros serviços; use `-p 3100`.

## Publicar no final-project

```powershell
cd ..\final-project
python scripts\exportar_ui.py
```

O script ativa `NEXT_EXPORT=1`, roda `next build` (com `output: "export"` e
`trailingSlash`) e copia `out` para `../final-project/ui`. Depois, recarregue
http://127.0.0.1:8000.

## Contrato da API

| Método | Rota                                        |
| ------ | ------------------------------------------- |
| GET    | `/api/ufs`                                  |
| GET    | `/api/municipios?uf=XX`                     |
| GET    | `/api/estatisticas?uf=XX&municipio=Nome`    |
| POST   | `/api/analise`                              |
| GET    | `/api/panorama`                             |
| GET    | `/api/health`                               |

O POST `/api/analise` recebe:

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

Resposta: `analise` (Markdown), `modelo`, `dados`, `fonte` (`ia` ou
`fallback`) e, em fallback, `aviso`.

## Comportamentos

- A alternativa de cidade começa desligada.
- Compromissos com horário fixo (show, evento, jogo) desabilitam a alternativa;
  a análise foca em chegada, permanência e saída.
- A narrativa é renderizada com `react-markdown`.

## Build

```powershell
npm run build
```

Para gerar o export estático manualmente:

```powershell
$env:NEXT_EXPORT="1"; npm run build
```
