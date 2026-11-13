"""Leitura do contexto da viagem: compromisso fixo x destino flexível."""

from __future__ import annotations

import re
import unicodedata

_COMPROMISSO_FIXO = re.compile(
    r"\b("
    r"show|shows|concerto|festival|evento|jogo|partida|estadio|teatro|"
    r"casamento|formatura|conferencia|palestra|prova|entrevista|reuniao|"
    r"congresso|feira|festa|balada|aniversario|competicao|campeonato|"
    r"corrida|maratona|circo|exposicao|espetaculo|apresentacao"
    r")\b"
)


def _normalizar(texto: str) -> str:
    decomposto = unicodedata.normalize("NFD", (texto or "").lower())
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def tem_compromisso_fixo(objetivo: str) -> bool:
    """True para eventos/compromissos com horário e local definidos.

    Nesses casos trocar de cidade não é uma opção realista; a análise deve
    focar em precauções de chegada, permanência e saída.
    """
    return bool(_COMPROMISSO_FIXO.search(_normalizar(objetivo)))


def deve_sugerir_alternativa(ctx: dict) -> bool:
    """Só sugere outra cidade quando o usuário aceita e o destino é flexível."""
    if not ctx.get("aceita_alternativa"):
        return False
    return not tem_compromisso_fixo(ctx.get("objetivo") or "")
