"""Publica o export do Next em ui/."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FRONT = RAIZ.parent / "frontend-next"
SAIDA = FRONT / "out"
DESTINO = RAIZ / "ui"


def construir() -> None:
    if not (FRONT / "node_modules").is_dir():
        sys.exit(
            "Dependências do Next não instaladas. Rode: "
            "cd frontend-next && npm install"
        )

    print("Construindo export estático do Next...")
    ambiente = {**os.environ, "NEXT_EXPORT": "1"}
    resultado = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONT,
        env=ambiente,
        shell=(os.name == "nt"),
    )
    if resultado.returncode != 0:
        sys.exit(resultado.returncode)


def publicar() -> None:
    if not SAIDA.is_dir():
        sys.exit("Pasta frontend-next/out não encontrada após o build.")

    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    shutil.copytree(SAIDA, DESTINO)
    print(f"UI publicada em {DESTINO.relative_to(RAIZ)}")


if __name__ == "__main__":
    construir()
    publicar()
    print("Pronto. Recarregue http://127.0.0.1:8000")
