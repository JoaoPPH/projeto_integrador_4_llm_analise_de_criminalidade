"""Acesso ao PostgreSQL (Neon) com pool de conexões reaproveitado."""

from __future__ import annotations

from typing import Any, Sequence

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from .config import DATABASE_URL

TABELA = '"ocorrencias_criminalidade"'

FILTRO_ANO_VALIDO = (
    "data_referencia IS NOT NULL "
    "AND data_referencia < DATE_TRUNC('year', CURRENT_DATE)::date"
)

_pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=8,
    timeout=180,
    kwargs={
        "connect_timeout": 20,
        "row_factory": dict_row,
        "application_name": "rota-segura-api",
    },
    open=False,
)


def abrir_pool() -> None:
    """Inicia o pool em segundo plano (não bloqueia o boot da API)."""
    if _pool.closed:
        _pool.open(wait=False)


def fechar_pool() -> None:
    if not _pool.closed:
        _pool.close()


def consultar(
    sql: str,
    params: Sequence[Any] | None = None,
    *,
    timeout_s: int = 120,
) -> list[dict[str, Any]]:
    """Executa uma consulta e devolve as linhas como dicionários."""
    with _pool.connection() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(f"SET statement_timeout = {int(timeout_s) * 1000}")
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
