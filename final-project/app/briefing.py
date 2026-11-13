"""Briefing de segurança montado a partir dos dados oficiais (fallback sem IA)."""

from __future__ import annotations

import re

from .catalogo import nome_uf
from .categorias import categorias_presentes
from .contexto import deve_sugerir_alternativa, tem_compromisso_fixo


def fmt(valor: float | int) -> str:
    return f"{int(round(valor or 0)):,}".replace(",", ".")


def titulo_cidade(nome: str) -> str:
    if not nome:
        return nome
    if nome == nome.upper() or nome == nome.lower():
        preposicoes = {"da", "de", "do", "das", "dos", "e"}
        partes = re.split(r"(\s|-)", nome.lower())
        saida = []
        for parte in partes:
            if len(parte) > 2 and parte not in preposicoes:
                saida.append(parte[0].upper() + parte[1:])
            else:
                saida.append(parte)
        return "".join(saida)
    return nome


def _recomendacoes_contexto(ctx: dict, cats: dict[str, int]) -> list[str]:
    r: list[str] = []
    periodo = (ctx.get("periodo") or "").lower()
    noturno = bool(re.search(r"noite|madrugada", periodo))

    if noturno:
        r.append(
            "No período noturno, prefira vias movimentadas e bem iluminadas e "
            "evite atalhos por áreas isoladas."
        )
    else:
        r.append(
            "Mesmo durante o dia, mantenha atenção a pertences em locais de "
            "grande circulação."
        )

    transporte = (ctx.get("meio_transporte") or "").lower()
    if "moto" in transporte:
        r.append(
            "De moto, não pare em pontos ermos, mantenha o capacete afivelado "
            "e desconfie de abordagens em semáforos."
        )
    elif "carro" in transporte:
        r.append(
            "De carro, mantenha vidros fechados e portas travadas em semáforos "
            "à noite e estacione em locais vigiados."
        )
    elif "pé" in transporte or "pe" in transporte:
        r.append(
            "A pé, evite exibir celular e objetos de valor e mantenha a bolsa à "
            "frente do corpo."
        )
    elif "público" in transporte or "publico" in transporte:
        r.append(
            "No transporte público, fique atento em embarques e desembarques e "
            "evite vagões ou pontos vazios à noite."
        )

    acompanhantes = (ctx.get("acompanhantes") or "").lower()
    if "sozinho" in acompanhantes:
        r.append(
            "Viajando sozinho, compartilhe sua localização em tempo real com "
            "alguém de confiança."
        )
    elif "família" in acompanhantes or "familia" in acompanhantes:
        r.append(
            "Com a família, combine um ponto de encontro caso o grupo se separe "
            "e redobre a atenção com crianças."
        )
    elif "amigos" in acompanhantes:
        r.append(
            "Em grupo, mantenham-se juntos ao circular por áreas desconhecidas."
        )

    top_cat = max(cats.items(), key=lambda item: item[1])[0] if cats else None
    if top_cat == "veiculos":
        r.append(
            "O destino concentra crimes contra veículos: use estacionamentos "
            "fechados e evite deixar objetos à vista."
        )
    elif top_cat == "roubos":
        r.append(
            "Roubos e furtos aparecem com destaque: distribua documentos e "
            "dinheiro e evite grandes saques em caixas na rua."
        )
    elif top_cat == "letal":
        r.append(
            "Há registros expressivos de violência letal: evite se envolver em "
            "conflitos e afaste-se de aglomerações tensas."
        )
    elif top_cat == "drogas":
        r.append(
            "O destino registra ocorrências ligadas ao tráfico: informe-se sobre "
            "áreas a evitar com moradores ou a hospedagem."
        )

    if tem_compromisso_fixo(ctx.get("objetivo") or ""):
        r.append(
            "Para um compromisso com horário fixo, chegue com antecedência e "
            "combine um ponto de encontro com o grupo."
        )
        r.append(
            "Na saída do evento, prefira transporte por aplicativo ou táxi de "
            "ponto oficial e evite caminhar sozinho por ruas vazias."
        )
        if "carro" in transporte:
            r.append(
                "Estacione em local vigiado e iluminado, guarde o comprovante e "
                "não deixe objetos à vista no veículo."
            )

    objetivo = (ctx.get("objetivo") or "").lower()
    if "turismo" in objetivo:
        r.append(
            "Para turismo, prefira pontos consolidados e contrate transporte por "
            "aplicativo em vez de táxis de rua desconhecidos."
        )
    elif "moradia" in objetivo:
        r.append(
            "Para moradia, pesquise a reputação do bairro e converse com "
            "vizinhos antes de fechar contrato."
        )
    elif "trabalho" in objetivo or "estudo" in objetivo:
        r.append(
            "Com deslocamentos de rotina, varie trajetos e horários sempre que "
            "possível."
        )

    return r


def montar_briefing(
    estat: dict, ctx: dict, perfil: dict | None = None
) -> str:
    destino = estat["destino"]
    alternativa = estat.get("alternativa")
    cidade = titulo_cidade(destino["municipio"])
    uf = nome_uf(destino["uf"])

    top = sorted(
        destino["detalhes_eventos"].items(), key=lambda item: item[1], reverse=True
    )[:6]

    cats = categorias_presentes(destino["detalhes_eventos"])
    recs = _recomendacoes_contexto(ctx, cats)

    linhas_top = "\n".join(
        f"- {evento} — **{fmt(valor)}** ocorrências" for evento, valor in top
    )

    partes: list[str] = []

    partes.append(f"## {cidade} ({destino['uf']}): leitura de segurança")
    partes.append(
        "Perfil considerado: deslocamento de "
        f"**{(ctx.get('meio_transporte') or '').lower()}**, "
        f"**{(ctx.get('acompanhantes') or '').lower()}**, "
        f"no período da **{(ctx.get('periodo') or '').lower()}**, "
        f"com objetivo de **{(ctx.get('objetivo') or '').lower()}**."
    )
    partes.append(
        f"Nos registros oficiais, {cidade} soma "
        f"**{fmt(destino['total_geral'])} registros** "
        f"({fmt(destino.get('total_ocorrencias', 0))} ocorrências e "
        f"{fmt(destino.get('total_vitimas', 0))} vítimas) no período analisado. "
        "Os tipos mais frequentes são:"
    )
    partes.append(linhas_top)

    if perfil:
        periodo = perfil.get("periodo") or {}
        if periodo.get("inicio") and periodo.get("fim"):
            partes.append(
                f"Os dados cobrem de **{periodo['inicio']}** a "
                f"**{periodo['fim']}**."
            )

        completos = [
            ano for ano in perfil.get("evolucao_anual", []) if not ano.get("parcial")
        ]
        if len(completos) >= 2:
            primeiro, ultimo = completos[0], completos[-1]
            inicio = primeiro["ocorrencias"] + primeiro["vitimas"]
            fim = ultimo["ocorrencias"] + ultimo["vitimas"]
            if inicio > 0:
                variacao = (fim - inicio) / inicio * 100
                direcao = "caiu" if variacao < 0 else "subiu"
                partes.append(
                    f"Nos anos completos, o volume {direcao} de "
                    f"**{fmt(inicio)}** registros em {primeiro['ano']} para "
                    f"**{fmt(fim)}** em {ultimo['ano']}."
                )

    partes.append("### Recomendações para o seu contexto")
    partes.append("\n".join(f"- {r}" for r in recs))

    if alternativa and deve_sugerir_alternativa(ctx):
        partes.append("### Alternativa mais tranquila")
        partes.append(
            f"Se houver flexibilidade, **{titulo_cidade(alternativa['municipio'])}** "
            f"é o município de menor incidência registrada em {uf}, com apenas "
            f"**{fmt(alternativa['total_geral'])} ocorrências** — bem abaixo de "
            f"{cidade}."
        )

    partes.append(
        "> Esta é uma análise automática baseada nos dados históricos de "
        "ocorrências. Ela é orientativa e não substitui as informações das "
        "autoridades de segurança locais."
    )

    return "\n\n".join(partes)
