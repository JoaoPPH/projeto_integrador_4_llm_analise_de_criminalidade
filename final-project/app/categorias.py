"""Agrupamento de eventos em categorias de risco."""

from __future__ import annotations

import re

CATEGORIAS = [
    (
        "policial",
        "Ações policiais e administrativas",
        re.compile(
            r"mandado|apreens|alvar|vistoria|atendimento|busca e salvamento|"
            r"combate a inc|pessoa desaparecida|pessoa localizada|emiss",
            re.I,
        ),
    ),
    ("transito", "Mortes no trânsito", re.compile(r"tr[aâ]nsito", re.I)),
    (
        "letal",
        "Violência letal",
        re.compile(
            r"homic|latroc|feminic|les[aã]o corporal seguida|"
            r"morte por intervenção|mortes a esclarecer",
            re.I,
        ),
    ),
    ("sexual", "Violência sexual", re.compile(r"estupro", re.I)),
    ("veiculos", "Crimes contra veículos", re.compile(r"ve[ií]culo", re.I)),
    ("roubos", "Roubos e furtos", re.compile(r"roubo|furto", re.I)),
    (
        "drogas",
        "Tráfico e drogas",
        re.compile(r"tr[aá]fico|coca|macon|droga", re.I),
    ),
    ("armas", "Armas de fogo", re.compile(r"arma", re.I)),
    ("agentes", "Agentes do Estado", re.compile(r"agente do estado", re.I)),
    ("suicidio", "Suicídio", re.compile(r"suic[ií]dio", re.I)),
]

ROTULOS = {chave: rotulo for chave, rotulo, _ in CATEGORIAS}
ROTULOS["outros"] = "Outros"


def classificar(evento: str) -> str:
    for chave, _rotulo, termos in CATEGORIAS:
        if termos.search(evento):
            return chave
    return "outros"


def resumo(ocorrencias: dict[str, int], vitimas: dict[str, int]) -> list[dict]:
    acumulado = {
        chave: {"categoria": rotulo, "ocorrencias": 0, "vitimas": 0}
        for chave, rotulo in ROTULOS.items()
    }

    for evento in set(ocorrencias) | set(vitimas):
        chave = classificar(evento)
        acumulado[chave]["ocorrencias"] += int(ocorrencias.get(evento, 0))
        acumulado[chave]["vitimas"] += int(vitimas.get(evento, 0))

    resultado = []
    for item in acumulado.values():
        total = item["ocorrencias"] + item["vitimas"]
        if total <= 0:
            continue
        item["total"] = total
        resultado.append(item)

    return sorted(resultado, key=lambda item: item["total"], reverse=True)


def categorias_presentes(detalhes: dict[str, int]) -> dict[str, int]:
    somas: dict[str, int] = {}
    for evento, valor in detalhes.items():
        for chave, _rotulo, termos in CATEGORIAS:
            if termos.search(evento):
                somas[chave] = somas.get(chave, 0) + valor
    return somas
