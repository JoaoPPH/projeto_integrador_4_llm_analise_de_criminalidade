"""Agregações nacionais do panorama (equivalente ao antigo app/api/panorama/route.ts)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .cache import CacheTTL
from .config import CACHE_PANORAMA_S
from .db import FILTRO_ANO_VALIDO, TABELA, consultar

_cache = CacheTTL()

SQLS = {
    "resumo": f"""
        SELECT COUNT(*)::bigint AS registros,
               COUNT(DISTINCT uf)::int AS estados,
               COUNT(DISTINCT municipio)::int AS municipios,
               MIN(EXTRACT(YEAR FROM data_referencia))::int AS ano_min,
               MAX(CASE WHEN {FILTRO_ANO_VALIDO}
                        THEN EXTRACT(YEAR FROM data_referencia) END)::int AS ano_max
        FROM {TABELA}
    """,
    "por_estado": f"""
        SELECT uf, SUM(total)::bigint AS total
        FROM {TABELA} WHERE {FILTRO_ANO_VALIDO}
        GROUP BY uf ORDER BY total DESC
    """,
    "evolucao": f"""
        SELECT EXTRACT(YEAR FROM data_referencia)::int AS ano,
               SUM(total)::bigint AS total
        FROM {TABELA} WHERE {FILTRO_ANO_VALIDO}
        GROUP BY ano ORDER BY ano
    """,
    "genero": f"""
        SELECT SUM(masculino)::bigint AS masculino,
               SUM(feminino)::bigint AS feminino,
               SUM(nao_informado)::bigint AS nao_informado
        FROM {TABELA} WHERE {FILTRO_ANO_VALIDO}
    """,
    "armas": f"""
        SELECT arma, SUM(total)::bigint AS total
        FROM {TABELA}
        WHERE {FILTRO_ANO_VALIDO}
          AND evento = 'Arma de Fogo Apreendida'
          AND arma IS NOT NULL
        GROUP BY arma ORDER BY total DESC
    """,
    "agentes": f"""
        SELECT agente, SUM(total_vitima)::bigint AS total
        FROM {TABELA}
        WHERE {FILTRO_ANO_VALIDO}
          AND evento IN ('Morte de Agente do Estado',
                         'Suicidio de Agente do Estado')
          AND agente IS NOT NULL
        GROUP BY agente ORDER BY total DESC
    """,
    "drogas": f"""
        SELECT EXTRACT(YEAR FROM data_referencia)::int AS ano,
               CASE WHEN LOWER(evento) LIKE '%coca%'
                    THEN 'Cocaína' ELSE 'Maconha' END AS droga,
               SUM(total_peso) AS peso_kg
        FROM {TABELA}
        WHERE {FILTRO_ANO_VALIDO}
          AND (LOWER(evento) LIKE '%coca%' OR LOWER(evento) LIKE '%macon%')
        GROUP BY ano, droga ORDER BY ano
    """,
}


def _int(valor: Any) -> int:
    return int(valor) if valor is not None else 0


def _float(valor: Any) -> float:
    return float(valor) if valor is not None else 0.0


def montar_panorama() -> dict:
    with ThreadPoolExecutor(max_workers=3) as executor:
        futuros = {
            nome: executor.submit(consultar, sql, timeout_s=240)
            for nome, sql in SQLS.items()
        }
        resultado = {nome: futuro.result() for nome, futuro in futuros.items()}

    resumo = resultado["resumo"][0]
    genero = resultado["genero"][0]

    drogas_por_ano: dict[int, dict[str, float]] = {}
    for linha in resultado["drogas"]:
        ano = _int(linha["ano"])
        atual = drogas_por_ano.setdefault(
            ano, {"ano": ano, "cocaina": 0.0, "maconha": 0.0}
        )
        toneladas = _float(linha["peso_kg"]) / 1000
        if linha["droga"] == "Cocaína":
            atual["cocaina"] = toneladas
        else:
            atual["maconha"] = toneladas

    return {
        "resumo": {
            "registros": _int(resumo["registros"]),
            "estados": _int(resumo["estados"]),
            "municipios": _int(resumo["municipios"]),
            "ano_min": _int(resumo["ano_min"]),
            "ano_max": _int(resumo["ano_max"]),
        },
        "por_estado": [
            {"uf": linha["uf"], "total": _int(linha["total"])}
            for linha in resultado["por_estado"]
        ],
        "evolucao": [
            {"ano": _int(linha["ano"]), "total": _int(linha["total"])}
            for linha in resultado["evolucao"]
        ],
        "genero": {
            "masculino": _int(genero["masculino"]),
            "feminino": _int(genero["feminino"]),
            "nao_informado": _int(genero["nao_informado"]),
        },
        "armas": [
            {"arma": linha["arma"], "total": _int(linha["total"])}
            for linha in resultado["armas"]
        ],
        "agentes": [
            {"agente": linha["agente"], "total": _int(linha["total"])}
            for linha in resultado["agentes"]
        ],
        "drogas": sorted(drogas_por_ano.values(), key=lambda d: d["ano"]),
    }


def obter_panorama() -> dict:
    return _cache.ou_calcular("panorama", CACHE_PANORAMA_S, montar_panorama)
