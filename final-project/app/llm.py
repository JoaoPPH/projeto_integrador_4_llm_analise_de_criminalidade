"""Cliente Groq e montagem do prompt."""

from __future__ import annotations

import json

import httpx

from .cache import CacheTTL
from .briefing import fmt
from .categorias import resumo as resumo_categorias
from .config import (
    CACHE_ANALISE_S,
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_TIMEOUT_S,
)
from .contexto import deve_sugerir_alternativa, tem_compromisso_fixo

_cache = CacheTTL()


class LLMError(Exception):
    """Falha ao obter a análise do provedor de IA."""


SYSTEM_PROMPT = """Você é um analista sênior de segurança pública brasileira.
Sua função é interpretar registros oficiais de criminalidade e produzir uma
leitura de segurança personalizada para viajantes e moradores.

Regras:
- Responda sempre em português do Brasil, em markdown claro e organizado.
- Baseie cada afirmação exclusivamente nos números fornecidos.
- Nunca invente estatísticas, localidades ou ocorrências.
- Seja objetivo, prático e empático; priorize o que reduz risco real.
- Quando os dados forem insuficientes, diga isso com honestidade."""


def provedor_disponivel() -> bool:
    """True quando a credencial do Groq está configurada."""
    return bool(LLM_API_KEY and LLM_BASE_URL)


def _percentual(parte: int, total: int) -> str:
    if not total:
        return "0%"
    return f"{(parte / total) * 100:.1f}%".replace(".", ",")


def _resumo_grupos(det_oc: dict, det_vi: dict, total: int) -> list[dict]:
    grupos = []
    for item in resumo_categorias(det_oc, det_vi):
        grupos.append(
            {
                "grupo": item["categoria"],
                "ocorrencias": item["ocorrencias"],
                "vitimas": item["vitimas"],
                "total": item["total"],
                "participacao": _percentual(item["total"], total),
            }
        )
    return grupos


def _dados_para_prompt(
    estat: dict, ctx: dict, perfil: dict | None = None
) -> dict:
    destino = estat["destino"]
    alternativa = estat.get("alternativa")
    total = destino.get("total_geral", 0)
    total_oc = destino.get("total_ocorrencias", total)
    total_vi = destino.get("total_vitimas", 0)
    det_oc = destino.get("detalhes_ocorrencias") or destino["detalhes_eventos"]
    det_vi = destino.get("detalhes_vitimas") or {}

    objetivo = ctx.get("objetivo") or "Não informado"
    compromisso_fixo = tem_compromisso_fixo(objetivo)
    tem_alternativa = bool(
        deve_sugerir_alternativa(ctx)
        and alternativa
        and alternativa.get("total_geral", 0) > 0
    )

    eventos = sorted(
        destino["detalhes_eventos"].items(), key=lambda item: item[1], reverse=True
    )
    top_eventos = []
    for evento, valor in eventos[:20]:
        vi = int(det_vi.get(evento, 0))
        top_eventos.append(
            {
                "evento": evento,
                "ocorrencias": int(det_oc.get(evento, 0)),
                "vitimas": vi,
                "total": valor,
                "participacao_total": _percentual(valor, total),
                "participacao_vitimas": _percentual(vi, total_vi),
            }
        )

    perfil = perfil or {}
    evolucao = perfil.get("evolucao_anual") or []
    genero = dict(perfil.get("genero") or {})
    periodo = perfil.get("periodo") or {}

    total_genero = sum(int(genero.get(chave, 0)) for chave in (
        "masculino", "feminino", "nao_informado"
    ))
    if total_genero:
        for chave in ("masculino", "feminino", "nao_informado"):
            genero[f"participacao_{chave}"] = _percentual(
                int(genero.get(chave, 0)), total_genero
            )

    dados = {
        "contexto_destino": {
            "uf": destino["uf"],
            "municipio": destino["municipio"],
            "periodo": {
                "inicio": periodo.get("inicio"),
                "fim": periodo.get("fim"),
                "ultimo_ano_parcial": any(a.get("parcial") for a in evolucao),
            },
            "total_geral": total,
            "total_ocorrencias": total_oc,
            "total_vitimas": total_vi,
            "tipos_de_ocorrencia": len(eventos),
            "eventos_mais_frequentes": top_eventos,
            "grupos": _resumo_grupos(det_oc, det_vi, total),
            "evolucao_anual": evolucao,
            "vitimas_por_genero": genero,
        },
        "sugestao_alternativa": None,
        "contexto_usuario": {
            "meio_transporte": ctx.get("meio_transporte") or "Não informado",
            "acompanhantes": ctx.get("acompanhantes") or "Não informado",
            "periodo": ctx.get("periodo") or "Não informado",
            "objetivo": objetivo,
            "compromisso_fixo": compromisso_fixo,
            "alternativa_solicitada": tem_alternativa,
        },
    }

    if tem_alternativa:
        alt_total = alternativa.get("total_geral", 0)
        alt_oc = alternativa.get("total_ocorrencias", alt_total)
        alt_vi = alternativa.get("total_vitimas", 0)
        alt_det_oc = (
            alternativa.get("detalhes_ocorrencias")
            or alternativa["detalhes_eventos"]
        )
        alt_det_vi = alternativa.get("detalhes_vitimas") or {}
        alt_eventos = sorted(
            alternativa["detalhes_eventos"].items(),
            key=lambda item: item[1],
            reverse=True,
        )[:8]
        reducao = "sem base de comparação"
        if total > 0:
            reducao = (
                f"{(1 - alt_total / total) * 100:.1f}%".replace(".", ",")
            )
        dados["sugestao_alternativa"] = {
            "uf": alternativa["uf"],
            "municipio": alternativa["municipio"],
            "total_geral": alt_total,
            "total_ocorrencias": alt_oc,
            "total_vitimas": alt_vi,
            "reducao_em_relacao_ao_destino": reducao,
            "eventos_mais_frequentes": [
                {
                    "evento": evento,
                    "ocorrencias": int(alt_det_oc.get(evento, 0)),
                    "vitimas": int(alt_det_vi.get(evento, 0)),
                    "total": valor,
                }
                for evento, valor in alt_eventos
            ],
            "grupos": _resumo_grupos(alt_det_oc, alt_det_vi, alt_total),
        }

    return dados


def montar_prompt(dados: dict) -> str:
    destino = dados["contexto_destino"]
    usuario = dados["contexto_usuario"]
    alternativa = dados["sugestao_alternativa"]
    periodo = destino.get("periodo") or {}
    genero = destino.get("vitimas_por_genero") or {}
    evolucao = destino.get("evolucao_anual") or []

    if periodo.get("inicio") and periodo.get("fim"):
        texto_periodo = f"de {periodo['inicio']} a {periodo['fim']}"
        if periodo.get("ultimo_ano_parcial"):
            texto_periodo += "; o último ano é parcial"
    else:
        texto_periodo = "não informado"

    linhas_eventos = "\n".join(
        f"  - {item['evento']}: {fmt(item['total'])} registros — "
        f"{fmt(item['vitimas'])} vítimas "
        f"({item['participacao_total']} dos registros; "
        f"{item['participacao_vitimas']} das vítimas)"
        for item in destino["eventos_mais_frequentes"]
    ) or "  - não informado"

    linhas_grupos = "\n".join(
        f"  - {g['grupo']}: {fmt(g['total'])} registros — "
        f"{fmt(g['vitimas'])} vítimas ({g['participacao']} dos registros)"
        for g in destino.get("grupos", [])
    ) or "  - não informado"

    linhas_anos = "\n".join(
        f"  - {a['ano']}{' (parcial)' if a.get('parcial') else ''}: "
        f"{fmt(a['ocorrencias'])} ocorrências / {fmt(a['vitimas'])} vítimas"
        for a in evolucao
    ) or "  - não informado"

    if genero:
        texto_genero = (
            f"- Masculino: {fmt(genero.get('masculino', 0))} "
            f"({genero.get('participacao_masculino', '0%')})\n"
            f"- Feminino: {fmt(genero.get('feminino', 0))} "
            f"({genero.get('participacao_feminino', '0%')})\n"
            f"- Não informado: {fmt(genero.get('nao_informado', 0))} "
            f"({genero.get('participacao_nao_informado', '0%')})"
        )
    else:
        texto_genero = "- não informado"

    bloco_alternativa = ""
    if alternativa:
        linhas_alt = "\n".join(
            f"  - {i['evento']}: {fmt(i['total'])} registros — "
            f"{fmt(i['vitimas'])} vítimas"
            for i in alternativa["eventos_mais_frequentes"]
        ) or "  - não informado"
        linhas_alt_grupos = "\n".join(
            f"  - {g['grupo']}: {fmt(g['total'])} registros — "
            f"{fmt(g['vitimas'])} vítimas"
            for g in alternativa.get("grupos", [])
        ) or "  - não informado"
        bloco_alternativa = f"""
## ALTERNATIVA MAIS TRANQUILA NO MESMO ESTADO ({alternativa['municipio']}/{alternativa['uf']})
- Registros: {fmt(alternativa['total_geral'])} ({fmt(alternativa['total_ocorrencias'])} ocorrências + {fmt(alternativa['total_vitimas'])} vítimas)
- Redução em relação ao destino: {alternativa['reducao_em_relacao_ao_destino']}
- Eventos mais frequentes:
{linhas_alt}
- Grupos:
{linhas_alt_grupos}
"""

    if usuario["compromisso_fixo"]:
        orientacao_fixa = (
            "O destino é um compromisso com horário/local fixo (ex.: show, "
            "evento, jogo). NÃO sugira trocar de cidade. Concentre-se em "
            "chegada, permanência e saída: transporte, estacionamento, ponto "
            "de encontro, horário de encerramento, bateria do celular e "
            "documentos."
        )
        exemplo_evento = (
            " Por ser um evento, inclua cuidados como chegar com antecedência, "
            "combinar um ponto de encontro, usar aplicativo ou táxi oficial na "
            "saída e evitar caminhadas solitárias."
        )
    else:
        orientacao_fixa = (
            "Se o destino não for um compromisso fixo, considere a "
            "flexibilidade da viagem antes de sugerir mudanças de rota."
        )
        exemplo_evento = ""

    if usuario["alternativa_solicitada"]:
        orientacao_alt = (
            "Compare o destino com a alternativa usando os totais e a redução "
            "percentual; recomende-a apenas se houver flexibilidade real."
        )
        formato_alt = (
            "### Alternativa mais tranquila\n"
            "Compare o destino com a alternativa usando os totais e a redução "
            "percentual.\n\n"
        )
    else:
        orientacao_alt = (
            "Não sugira outra cidade e não inclua seção de alternativa; o foco "
            "é reduzir risco no destino escolhido."
        )
        formato_alt = ""

    return f"""Analise os dados oficiais abaixo e produza uma leitura de segurança
personalizada para o contexto da viagem.

## DESTINO ({destino['municipio']}/{destino['uf']})
- Período dos dados: {texto_periodo}
- Registros totais: {fmt(destino['total_geral'])} ({fmt(destino['total_ocorrencias'])} ocorrências + {fmt(destino['total_vitimas'])} vítimas)
- Tipos distintos de ocorrência: {destino['tipos_de_ocorrencia']}

## EVENTOS MAIS FREQUENTES (ocorrências / vítimas)
{linhas_eventos}

## GRUPOS DE OCORRÊNCIA
{linhas_grupos}

## EVOLUÇÃO ANUAL (ocorrências / vítimas)
{linhas_anos}

## VÍTIMAS POR GÊNERO
{texto_genero}
{bloco_alternativa}
## CONTEXTO DO USUÁRIO
- Meio de transporte: {usuario['meio_transporte']}
- Acompanhantes: {usuario['acompanhantes']}
- Período da viagem: {usuario['periodo']}
- Objetivo: {usuario['objetivo']}
- Compromisso com horário/local fixo: {"sim" if usuario['compromisso_fixo'] else "não"}
- Alternativa de cidade solicitada: {"sim" if usuario['alternativa_solicitada'] else "não"}

## ORIENTAÇÕES
1. Use apenas os números fornecidos; não invente estatísticas.
2. Os registros combinam a coluna de ocorrências (ações/registros) e a de
   vítimas. Quando uma coluna é 0, o evento é medido pela outra; nunca trate
   "0 ocorrências" como ausência de casos. Mandados, apreensões, alvarás,
   vistorias e atendimentos são ações policiais/administrativas.
3. Use a evolução anual para apontar tendência; trate o último ano como parcial
   e não projete valores.
4. Não compare cidades por volume absoluto sem dados de população.
5. Cada recomendação deve ser acionável para transporte, companhia, período e
   objetivo.{exemplo_evento}
6. {orientacao_fixa}
7. {orientacao_alt}
8. Se os dados forem insuficientes ou houver muito "Não informado", diga isso.

## FORMATO DA RESPOSTA
Use exatamente estas seções em markdown:
### Resumo executivo
Um parágrafo com a leitura geral, o período coberto e o que domina os registros.

### Leitura dos números
Explique a diferença entre ocorrências e vítimas, os grupos e a tendência anual,
citando os números e percentuais.

### Riscos para o seu contexto
Lista com os riscos mais relevantes para o transporte, a companhia, o período e
o objetivo informados.

### Recomendações práticas
De 5 a 8 recomendações acionáveis, vinculadas ao cenário informado.

{formato_alt}Seja direto, evite repetições e não ultrapasse cerca de 500 palavras."""


def _chamar_groq(prompt: str) -> tuple[str, str, int]:
    if not (LLM_API_KEY and LLM_BASE_URL):
        raise LLMError("Provedor Groq não configurado.")

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 2000,
        "top_p": 0.9,
    }

    try:
        with httpx.Client(timeout=LLM_TIMEOUT_S) as cliente:
            resposta = cliente.post(
                f"{LLM_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {LLM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.TimeoutException as exc:
        raise LLMError("O provedor de IA demorou demais para responder.") from exc
    except httpx.HTTPError as exc:
        raise LLMError("Não foi possível comunicar com o provedor de IA.") from exc

    if resposta.status_code >= 400:
        raise LLMError(
            f"O provedor de IA respondeu com erro {resposta.status_code}."
        )

    try:
        corpo = resposta.json()
        texto = (corpo["choices"][0]["message"]["content"] or "").strip()
        modelo = corpo.get("model") or LLM_MODEL
        tokens = int((corpo.get("usage") or {}).get("total_tokens", 0))
    except (ValueError, KeyError, TypeError, IndexError) as exc:
        raise LLMError("O provedor de IA retornou uma resposta inválida.") from exc

    if not texto:
        raise LLMError("A resposta da IA veio vazia.")

    return texto, modelo, tokens


def analisar_criminalidade(
    estat: dict, ctx: dict, perfil: dict | None = None
) -> dict:
    """Chama o provedor configurado e devolve análise + dados usados."""
    dados = _dados_para_prompt(estat, ctx, perfil)
    prompt = montar_prompt(dados)

    chave = json.dumps(
        {
            "destino": dados["contexto_destino"]["municipio"],
            "uf": dados["contexto_destino"]["uf"],
            "total_geral": dados["contexto_destino"]["total_geral"],
            "total_ocorrencias": dados["contexto_destino"]["total_ocorrencias"],
            "total_vitimas": dados["contexto_destino"]["total_vitimas"],
            "perfil": perfil or {},
            **dados["contexto_usuario"],
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    def calcular() -> dict:
        texto, modelo, tokens = _chamar_groq(prompt)

        return {
            "success": True,
            "analise": texto,
            "modelo": modelo,
            "tokens_utilizados": tokens,
            "dados": {
                "destino": estat["destino"],
                "alternativa": (
                    estat.get("alternativa")
                    if dados["contexto_usuario"]["alternativa_solicitada"]
                    else None
                ),
                "perfil": perfil or {},
                "contexto_usuario": dados["contexto_usuario"],
            },
        }

    return _cache.ou_calcular(("analise", chave), CACHE_ANALISE_S, calcular)
