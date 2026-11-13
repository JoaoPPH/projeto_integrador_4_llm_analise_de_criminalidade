"""Renderizador Markdown seguro."""

from __future__ import annotations

import html
import re

_BLOCO_ESPECIAL = re.compile(
    r"^(#{1,6}\s|>\s?|[-*]\s+|\d+\.\s+|(-{3,}|\*{3,})$)"
)


def _inline(texto: str) -> str:
    seguro = html.escape(texto, quote=False)

    seguro = re.sub(
        r"`([^`]+)`",
        lambda m: f"<code>{m.group(1)}</code>",
        seguro,
    )
    seguro = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", seguro)
    seguro = re.sub(
        r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)",
        r"<em>\1</em>",
        seguro,
    )
    return seguro


def renderizar(texto: str) -> str:
    linhas = (texto or "").replace("\r\n", "\n").split("\n")
    saida: list[str] = []
    i = 0

    while i < len(linhas):
        linha = linhas[i].strip()

        if not linha:
            i += 1
            continue

        titulo = re.match(r"^(#{1,6})\s+(.*)$", linha)
        if titulo:
            nivel = len(titulo.group(1))
            saida.append(f"<h{nivel}>{_inline(titulo.group(2))}</h{nivel}>")
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,})$", linha):
            saida.append("<hr>")
            i += 1
            continue

        if linha.startswith(">"):
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith(">"):
                bloco.append(linhas[i].strip()[1:].strip())
                i += 1
            saida.append(
                "<blockquote>" + " ".join(_inline(b) for b in bloco) + "</blockquote>"
            )
            continue

        if re.match(r"^[-*]\s+", linha):
            itens = []
            while i < len(linhas) and re.match(r"^[-*]\s+", linhas[i].strip()):
                itens.append(re.sub(r"^[-*]\s+", "", linhas[i].strip()))
                i += 1
            saida.append(
                "<ul>" + "".join(f"<li>{_inline(x)}</li>" for x in itens) + "</ul>"
            )
            continue

        if re.match(r"^\d+\.\s+", linha):
            itens = []
            while i < len(linhas) and re.match(r"^\d+\.\s+", linhas[i].strip()):
                itens.append(re.sub(r"^\d+\.\s+", "", linhas[i].strip()))
                i += 1
            saida.append(
                "<ol>" + "".join(f"<li>{_inline(x)}</li>" for x in itens) + "</ol>"
            )
            continue

        paragrafo = []
        while i < len(linhas):
            atual = linhas[i].strip()
            if not atual or _BLOCO_ESPECIAL.match(atual):
                break
            paragrafo.append(atual)
            i += 1

        if not paragrafo:
            paragrafo = [linha]
            i += 1

        saida.append(
            "<p>" + " ".join(_inline(p) for p in paragrafo) + "</p>"
        )

    return "\n".join(saida)
