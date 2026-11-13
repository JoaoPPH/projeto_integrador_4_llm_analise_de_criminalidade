"use client";

import { MapPin, Layers, TrendingDown, ArrowRight } from "lucide-react";
import BarraHorizontal from "@/components/charts/BarraHorizontal";
import { fmt, tituloCidade } from "@/lib/format";
import { nomeUf } from "@/lib/ufs";

export interface EstatMunicipio {
  uf: string;
  municipio: string;
  total_geral: number;
  detalhes_eventos: Record<string, number>;
}

export interface Estatisticas {
  destino: EstatMunicipio;
  alternativa: EstatMunicipio | null;
}

function topEventos(detalhes: Record<string, number>, n = 7) {
  return Object.entries(detalhes)
    .map(([nome, valor]) => ({ nome, valor }))
    .sort((a, b) => b.valor - a.valor)
    .slice(0, n);
}

export default function PainelDestino({
  estat,
  mostrarAlternativa = true,
}: {
  estat: Estatisticas;
  mostrarAlternativa?: boolean;
}) {
  const { destino, alternativa } = estat;
  const eventos = topEventos(destino.detalhes_eventos);
  const tiposCount = Object.keys(destino.detalhes_eventos).length;
  const dominante = eventos[0];

  return (
    <div className="space-y-5">
      <div className="panel rounded-2xl p-5">
        <div className="flex items-center gap-2 text-sm text-muted">
          <MapPin size={15} className="text-beacon" />
          <span>
            {tituloCidade(destino.municipio)} · {nomeUf(destino.uf)}
          </span>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3">
          <Metrica
            rotulo="Ocorrências registradas"
            valor={fmt(destino.total_geral)}
          />
          <Metrica
            rotulo="Tipos de ocorrência"
            valor={fmt(tiposCount)}
            icone={<Layers size={14} />}
          />
        </div>

        {dominante && (
          <p className="mt-4 text-sm leading-relaxed text-muted">
            Registro mais frequente:{" "}
            <span className="text-ink">{dominante.nome}</span>, com{" "}
            <span className="num text-beacon">{fmt(dominante.valor)}</span>{" "}
            ocorrências.
          </p>
        )}
      </div>

      {eventos.length > 0 && (
        <div className="panel rounded-2xl p-5">
          <h3 className="font-display text-[1.05rem] text-ink">
            Perfil das ocorrências
          </h3>
          <p className="mt-1 mb-3 text-xs text-faint">
            Tipos de registro mais comuns no destino
          </p>
          <BarraHorizontal dados={eventos} gradiente sufixo="reg." />
        </div>
      )}

      {alternativa && mostrarAlternativa && (
        <div className="rounded-2xl border border-cyan/35 bg-cyan/[0.06] p-5">
          <div className="flex items-center gap-2 text-sm text-cyan">
            <TrendingDown size={15} />
            <span>Destino mais tranquilo no mesmo estado</span>
          </div>
          <p className="mt-3 font-display text-xl text-ink">
            {tituloCidade(alternativa.municipio)}
          </p>
          <div className="mt-3 flex items-center gap-3 text-sm text-muted">
            <span>
              <span className="num text-ink">
                {fmt(alternativa.total_geral)}
              </span>{" "}
              ocorrências
            </span>
            <ArrowRight size={14} className="text-faint" />
            <span className="text-cyan">
              menor incidência registrada em {nomeUf(destino.uf)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

function Metrica({
  rotulo,
  valor,
  icone,
}: {
  rotulo: string;
  valor: string;
  icone?: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-line bg-canvas-2/60 px-4 py-3">
      <div className="flex items-center gap-1.5 text-[0.72rem] text-faint">
        {icone}
        <span>{rotulo}</span>
      </div>
      <p className="num mt-1 text-2xl font-semibold text-ink">{valor}</p>
    </div>
  );
}
