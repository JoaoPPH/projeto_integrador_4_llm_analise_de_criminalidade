"""Cache em memória com TTL."""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, Hashable


class CacheTTL:
    def __init__(self) -> None:
        self._dados: dict[Hashable, tuple[float, Any]] = {}
        self._trava = threading.Lock()
        self._chaves_em_calculo: dict[Hashable, threading.Lock] = {}

    def obter(self, chave: Hashable) -> Any | None:
        with self._trava:
            item = self._dados.get(chave)
            if item and item[0] > time.monotonic():
                return item[1]
        return None

    def guardar(self, chave: Hashable, valor: Any, ttl_s: int) -> None:
        with self._trava:
            self._dados[chave] = (time.monotonic() + ttl_s, valor)

    def ou_calcular(
        self,
        chave: Hashable,
        ttl_s: int,
        fabrica: Callable[[], Any],
    ) -> Any:
        """Devolve o valor cacheado ou calcula uma única vez por chave."""
        valor = self.obter(chave)
        if valor is not None:
            return valor

        with self._trava:
            trava = self._chaves_em_calculo.setdefault(chave, threading.Lock())

        try:
            with trava:
                valor = self.obter(chave)
                if valor is not None:
                    return valor

                valor = fabrica()
                self.guardar(chave, valor, ttl_s)
                return valor
        finally:
            with self._trava:
                self._chaves_em_calculo.pop(chave, None)
