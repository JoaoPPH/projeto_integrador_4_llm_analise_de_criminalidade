"""Perfil complementar do município: período, gênero e evolução anual."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date

from .cache import CacheTTL
from .config import CACHE_ESTATISTICAS_S
from .db import TABELA, consultar

_cache = CacheTTL()

_FILTRO = "uf = %s AND LOWER(municipio) = LOWER(%s)"

_SQL_RESUMO = f"""
    SELECT MIN(data_referencia) AS inicio,
           MAX(data_referencia) AS fim,
           SUM(COALESCE(masculino, 0))::bigint AS masculino,
           SUM(COALESCE(feminino, 0))::bigint AS feminino,
           SUM(COALESCE(nao_informado, 0))::bigint AS nao_informado
    FROM {TABELA}
    WHERE {_FILTRO}
"""

_SQL_ANOS = f"""
    SELECT EXTRACT(YEAR FROM data_referencia)::int AS ano,
           SUM(COALESCE(total, 0))::bigint AS ocorrencias,
           SUM(COALESCE(total_vitima, 0))::bigint AS vitimas
    FROM {TABELA}
    WHERE {_FILTRO} AND data_referencia IS NOT NULL
    GROUP BY ano
    ORDER BY ano
"""


def _iso(valor) -> str | None:
    return valor.isoformat() if isinstance(valor, date) else None


def obter_perfil(uf: str, municipio: str) -> dict:
    chave = ("perfil", uf.strip().upper(), municipio.strip().lower())

    def calcular() -> dict:
        params = [uf.strip().upper(), municipio.strip()]
        with ThreadPoolExecutor(max_workers=2) as executor:
            resumo_f = executor.submit(consultar, _SQL_RESUMO, params)
            anos_f = executor.submit(consultar, _SQL_ANOS, params)
            resumo = resumo_f.result()[0]
            anos = anos_f.result()

        ano_atual = date.today().year
        evolucao = []
        hist_oc = hist_vi = 0

        for linha in anos:
            ano = int(linha["ano"])
            parcial = ano >= ano_atual
            oc = int(linha["ocorrencias"] or 0)
            vi = int(linha["vitimas"] or 0)
            evolucao.append(
                {"ano": ano, "ocorrencias": oc, "vitimas": vi, "parcial": parcial}
            )
            if not parcial:
                hist_oc += oc
                hist_vi += vi

        return {
            "periodo": {
                "inicio": _iso(resumo.get("inicio")),
                "fim": _iso(resumo.get("fim")),
            },
            "genero": {
                "masculino": int(resumo.get("masculino") or 0),
                "feminino": int(resumo.get("feminino") or 0),
                "nao_informado": int(resumo.get("nao_informado") or 0),
            },
            "evolucao_anual": evolucao,
            "total_historico": {"ocorrencias": hist_oc, "vitimas": hist_vi},
        }

    return _cache.ou_calcular(chave, CACHE_ESTATISTICAS_S, calcular)
