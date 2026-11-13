"""Listas de estados e municípios para os seletores do frontend."""

from __future__ import annotations

from .cache import CacheTTL
from .config import CACHE_CATALOGO_S
from .db import TABELA, consultar

_cache = CacheTTL()

NOMES_UF = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}

INVALIDOS = {"NÃO INFORMADO", "NAO INFORMADO"}


def nome_uf(sigla: str) -> str:
    return NOMES_UF.get((sigla or "").upper(), sigla)


def listar_ufs() -> list[dict]:
    """Lista fixa dos 27 estados — não precisa consultar o banco."""
    return [{"sigla": sigla, "nome": NOMES_UF[sigla]} for sigla in sorted(NOMES_UF)]


def listar_municipios(uf: str) -> list[str]:
    chave = ("municipios", uf.upper())

    def calcular() -> list[str]:
        linhas = consultar(
            f"SELECT DISTINCT municipio FROM {TABELA} "
            "WHERE uf = %s AND municipio IS NOT NULL "
            "ORDER BY municipio",
            [uf.strip().upper()],
        )
        municipios = []
        for linha in linhas:
            nome = (linha["municipio"] or "").strip()
            if nome and nome.upper() not in INVALIDOS:
                municipios.append(nome)
        return municipios

    return _cache.ou_calcular(chave, CACHE_CATALOGO_S, calcular)
