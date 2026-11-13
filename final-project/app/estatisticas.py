"""Agregações por município com ocorrências e vítimas separadas."""

from __future__ import annotations

from .cache import CacheTTL
from .config import CACHE_ESTATISTICAS_S
from .db import TABELA, consultar

_cache = CacheTTL()

_CAMPOS = """
    evento,
    SUM(COALESCE(total, 0))::bigint AS ocorrencias,
    SUM(COALESCE(total_vitima, 0))::bigint AS vitimas
"""

_SQL_EVENTOS = f"""
    SELECT {_CAMPOS}
    FROM {TABELA}
    WHERE uf = %s AND municipio = %s
    GROUP BY evento
    HAVING SUM(COALESCE(total, 0)) + SUM(COALESCE(total_vitima, 0)) > 0
    ORDER BY SUM(COALESCE(total, 0)) + SUM(COALESCE(total_vitima, 0)) DESC
"""

_SQL_EVENTOS_CI = f"""
    SELECT {_CAMPOS}
    FROM {TABELA}
    WHERE LOWER(uf) = LOWER(%s) AND LOWER(municipio) = LOWER(%s)
    GROUP BY evento
    HAVING SUM(COALESCE(total, 0)) + SUM(COALESCE(total_vitima, 0)) > 0
    ORDER BY SUM(COALESCE(total, 0)) + SUM(COALESCE(total_vitima, 0)) DESC
"""


def _linhas_eventos(uf: str, municipio: str) -> list[dict]:
    sigla = uf.strip().upper()
    nome = municipio.strip()
    linhas = consultar(_SQL_EVENTOS, [sigla, nome])
    if not linhas:
        linhas = consultar(_SQL_EVENTOS_CI, [sigla, nome])
    return linhas


def obter_estatisticas_municipio(uf: str, municipio: str) -> dict:
    detalhes: dict[str, int] = {}
    ocorrencias: dict[str, int] = {}
    vitimas: dict[str, int] = {}
    total = total_oc = total_vi = 0

    for linha in _linhas_eventos(uf, municipio):
        evento = (linha.get("evento") or "").strip()
        oc = int(linha.get("ocorrencias") or 0)
        vi = int(linha.get("vitimas") or 0)
        if not evento or oc + vi <= 0:
            continue
        detalhes[evento] = oc + vi
        ocorrencias[evento] = oc
        vitimas[evento] = vi
        total += oc + vi
        total_oc += oc
        total_vi += vi

    return {
        "uf": uf,
        "municipio": municipio,
        "total_geral": total,
        "total_ocorrencias": total_oc,
        "total_vitimas": total_vi,
        "detalhes_eventos": detalhes,
        "detalhes_ocorrencias": ocorrencias,
        "detalhes_vitimas": vitimas,
    }


def buscar_municipio_alternativo(uf: str, municipio_atual: str) -> dict | None:
    linhas = consultar(
        f"""
        SELECT municipio
        FROM {TABELA}
        WHERE uf = %s
          AND LOWER(municipio) <> LOWER(%s)
          AND UPPER(municipio) NOT IN ('NÃO INFORMADO', 'NAO INFORMADO')
        GROUP BY municipio
        HAVING SUM(COALESCE(total, 0) + COALESCE(total_vitima, 0)) > 0
        ORDER BY SUM(COALESCE(total, 0) + COALESCE(total_vitima, 0)) ASC
        LIMIT 1
        """,
        [uf.strip().upper(), municipio_atual.strip()],
    )
    if not linhas:
        return None
    return obter_estatisticas_municipio(uf, linhas[0]["municipio"])


def obter_estatisticas(uf: str, municipio: str) -> dict:
    chave = ("estat", uf.strip().upper(), municipio.strip().lower())

    def calcular() -> dict:
        return {
            "destino": obter_estatisticas_municipio(uf, municipio),
            "alternativa": buscar_municipio_alternativo(uf, municipio),
        }

    return _cache.ou_calcular(chave, CACHE_ESTATISTICAS_S, calcular)
