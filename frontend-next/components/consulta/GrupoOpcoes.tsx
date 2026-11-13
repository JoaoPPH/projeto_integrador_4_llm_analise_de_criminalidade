"use client";

interface Props {
  rotulo: string;
  opcoes: string[];
  valor: string;
  aoMudar: (v: string) => void;
}

export default function GrupoOpcoes({ rotulo, opcoes, valor, aoMudar }: Props) {
  return (
    <fieldset>
      <legend className="mb-2 text-[0.82rem] font-medium text-muted">
        {rotulo}
      </legend>
      <div className="flex flex-wrap gap-2">
        {opcoes.map((o) => {
          const ativo = o === valor;
          return (
            <button
              key={o}
              type="button"
              aria-pressed={ativo}
              onClick={() => aoMudar(o)}
              className={`rounded-full border px-3.5 py-2 text-sm transition-all ${
                ativo
                  ? "border-beacon bg-beacon/15 text-beacon"
                  : "border-line bg-panel-2/50 text-muted hover:border-line-2 hover:text-ink"
              }`}
            >
              {o}
            </button>
          );
        })}
      </div>
    </fieldset>
  );
}
