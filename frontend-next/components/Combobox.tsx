"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronDown, Search, Check } from "lucide-react";

export interface OpcaoCombo {
  valor: string;
  rotulo: string;
  sub?: string;
}

interface Props {
  opcoes: OpcaoCombo[];
  valor: string | null;
  aoSelecionar: (valor: string) => void;
  placeholder: string;
  rotulo: string;
  desabilitado?: boolean;
  carregando?: boolean;
}

/** Combobox pesquisável e acessível (teclado + mouse), tema escuro. */
export default function Combobox({
  opcoes,
  valor,
  aoSelecionar,
  placeholder,
  rotulo,
  desabilitado,
  carregando,
}: Props) {
  const [aberto, setAberto] = useState(false);
  const [busca, setBusca] = useState("");
  const [destaque, setDestaque] = useState(0);
  const refRaiz = useRef<HTMLDivElement>(null);
  const refBusca = useRef<HTMLInputElement>(null);

  const selecionada = opcoes.find((o) => o.valor === valor) ?? null;

  const filtradas = useMemo(() => {
    const semAcento = (s: string) =>
      s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
    const q = semAcento(busca.trim());
    if (!q) return opcoes.slice(0, 200);
    return opcoes.filter((o) => semAcento(o.rotulo).includes(q)).slice(0, 200);
  }, [busca, opcoes]);

  useEffect(() => {
    if (aberto) {
      setBusca("");
      setDestaque(0);
      setTimeout(() => refBusca.current?.focus(), 10);
    }
  }, [aberto]);

  useEffect(() => {
    function aoClicarFora(e: MouseEvent) {
      if (refRaiz.current && !refRaiz.current.contains(e.target as Node)) {
        setAberto(false);
      }
    }
    document.addEventListener("mousedown", aoClicarFora);
    return () => document.removeEventListener("mousedown", aoClicarFora);
  }, []);

  function escolher(o: OpcaoCombo) {
    aoSelecionar(o.valor);
    setAberto(false);
  }

  function aoTeclar(e: React.KeyboardEvent) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setDestaque((d) => Math.min(d + 1, filtradas.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setDestaque((d) => Math.max(d - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (filtradas[destaque]) escolher(filtradas[destaque]);
    } else if (e.key === "Escape") {
      setAberto(false);
    }
  }

  return (
    <div className="relative" ref={refRaiz}>
      <label className="mb-2 block text-[0.82rem] font-medium text-muted">
        {rotulo}
      </label>
      <button
        type="button"
        disabled={desabilitado || carregando}
        onClick={() => setAberto((a) => !a)}
        className="flex w-full items-center justify-between gap-3 rounded-xl border border-line bg-panel-2/70 px-4 py-3.5 text-left transition-colors hover:border-line-2 disabled:cursor-not-allowed disabled:opacity-45"
      >
        <span className="min-w-0 flex-1">
          {selecionada ? (
            <span className="block truncate text-ink">{selecionada.rotulo}</span>
          ) : (
            <span className="block truncate text-faint">
              {carregando ? "Carregando…" : placeholder}
            </span>
          )}
        </span>
        <ChevronDown
          size={18}
          className={`shrink-0 text-muted transition-transform ${
            aberto ? "rotate-180" : ""
          }`}
        />
      </button>

      {aberto && (
        <div className="absolute z-30 mt-2 w-full overflow-hidden rounded-xl border border-line-2 bg-panel shadow-2xl shadow-black/50">
          <div className="flex items-center gap-2 border-b border-line px-3.5 py-2.5">
            <Search size={16} className="text-faint" />
            <input
              ref={refBusca}
              value={busca}
              onChange={(e) => {
                setBusca(e.target.value);
                setDestaque(0);
              }}
              onKeyDown={aoTeclar}
              placeholder="Buscar…"
              className="w-full bg-transparent text-sm text-ink placeholder:text-faint focus:outline-none"
            />
          </div>
          <ul className="max-h-64 overflow-y-auto py-1" role="listbox">
            {filtradas.length === 0 && (
              <li className="px-4 py-3 text-sm text-faint">
                Nenhum resultado.
              </li>
            )}
            {filtradas.map((o, i) => {
              const ativo = o.valor === valor;
              return (
                <li key={o.valor} role="option" aria-selected={ativo}>
                  <button
                    type="button"
                    onMouseEnter={() => setDestaque(i)}
                    onClick={() => escolher(o)}
                    className={`flex w-full items-center justify-between gap-2 px-4 py-2.5 text-left text-sm transition-colors ${
                      i === destaque ? "bg-panel-2" : ""
                    } ${ativo ? "text-beacon" : "text-ink"}`}
                  >
                    <span className="min-w-0">
                      <span className="block truncate">{o.rotulo}</span>
                      {o.sub && (
                        <span className="block truncate text-xs text-faint">
                          {o.sub}
                        </span>
                      )}
                    </span>
                    {ativo && <Check size={15} className="shrink-0" />}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
