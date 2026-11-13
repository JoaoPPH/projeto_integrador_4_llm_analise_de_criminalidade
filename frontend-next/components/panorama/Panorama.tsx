"use client";

import { useEffect, useState } from "react";
import {
  Database,
  MapPinned,
  Building2,
  CalendarRange,
  Radar,
} from "lucide-react";
import BarraHorizontal from "@/components/charts/BarraHorizontal";
import LinhaTemporal from "@/components/charts/LinhaTemporal";
import Rosca from "@/components/charts/Rosca";
import BarrasDrogas from "@/components/charts/BarrasDrogas";
import { fmt } from "@/lib/format";
import { nomeUf } from "@/lib/ufs";

interface DadosPanorama {
  resumo: {
    registros: number;
    estados: number;
    municipios: number;
    ano_min: number;
    ano_max: number;
  };
  por_estado: { uf: string; total: number }[];
  evolucao: { ano: number; total: number }[];
  genero: { masculino: number; feminino: number; nao_informado: number };
  armas: { arma: string; total: number }[];
  agentes: { agente: string; total: number }[];
  drogas: { ano: number; cocaina: number; maconha: number }[];
}

export default function Panorama() {
  const [dados, setDados] = useState<DadosPanorama | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/panorama")
      .then(async (r) => {
        const d = await r.json();
        if (!r.ok) throw new Error(d.error ?? "Falha ao carregar.");
        return d as DadosPanorama;
      })
      .then(setDados)
      .catch((e) => setErro(e.message));
  }, []);

  if (erro) {
    return (
      <div className="mx-auto max-w-6xl px-5 py-24">
        <p className="panel rounded-2xl p-6 text-muted">{erro}</p>
      </div>
    );
  }

  if (!dados) {
    return (
      <div className="mx-auto flex max-w-6xl flex-col items-center px-5 py-32 text-center">
        <span className="relative flex h-14 w-14 items-center justify-center">
          <span
            className="absolute inset-0 rounded-full"
            style={{
              background:
                "conic-gradient(from 0deg, transparent, rgba(255,194,71,0.5) 90deg, transparent 180deg)",
              animation: "sweep 1.4s linear infinite",
            }}
          />
          <span className="absolute inset-[3px] rounded-full bg-canvas" />
          <Radar size={22} className="relative text-beacon" />
        </span>
        <p className="mt-5 text-muted">Agregando milhões de ocorrências…</p>
      </div>
    );
  }

  const estados = dados.por_estado
    .slice(0, 12)
    .map((e) => ({ nome: nomeUf(e.uf), valor: e.total }));
  const armas = dados.armas
    .slice(0, 10)
    .map((a) => ({ nome: a.arma, valor: a.total }));
  const agentes = dados.agentes.map((a) => ({ nome: a.agente, valor: a.total }));
  const genero = [
    { nome: "Masculino", valor: dados.genero.masculino, cor: "#53c4e8" },
    { nome: "Feminino", valor: dados.genero.feminino, cor: "#e879c7" },
    { nome: "Não informado", valor: dados.genero.nao_informado, cor: "#64748b" },
  ];

  return (
    <div className="mx-auto max-w-6xl px-5 py-14">
      <header className="max-w-2xl">
        <h1 className="font-display text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
          Panorama nacional
        </h1>
        <p className="mt-4 text-lg leading-relaxed text-muted">
          A mesma base que alimenta a consulta por IA, vista de cima: a extensão
          dos registros de criminalidade pública do Brasil, por estado, período
          e natureza da ocorrência.
        </p>
      </header>

      <div className="mt-10 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Tile
          icone={<Database size={16} />}
          valor={fmt(dados.resumo.registros)}
          rotulo="Registros na base"
        />
        <Tile
          icone={<MapPinned size={16} />}
          valor={fmt(dados.resumo.estados)}
          rotulo="Estados"
        />
        <Tile
          icone={<Building2 size={16} />}
          valor={fmt(dados.resumo.municipios)}
          rotulo="Municípios"
        />
        <Tile
          icone={<CalendarRange size={16} />}
          valor={`${dados.resumo.ano_min}–${dados.resumo.ano_max}`}
          rotulo="Período coberto"
        />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Secao
          titulo="Ocorrências por estado"
          subtitulo="Soma total de ocorrências — 12 estados com maior volume"
        >
          <BarraHorizontal dados={estados} gradiente />
        </Secao>

        <Secao
          titulo="Evolução no tempo"
          subtitulo="Total de ocorrências registradas por ano"
        >
          <LinhaTemporal dados={dados.evolucao} />
        </Secao>

        <Secao
          titulo="Vítimas por gênero"
          subtitulo="Distribuição acumulada no período"
        >
          <Rosca dados={genero} />
        </Secao>

        <Secao
          titulo="Armas de fogo apreendidas"
          subtitulo="Quantidade por tipo de arma"
        >
          <BarraHorizontal dados={armas} cor="#53c4e8" sufixo="un." />
        </Secao>

        <Secao
          titulo="Mortes de agentes do Estado"
          subtitulo="Total de vítimas por tipo de agente"
        >
          <BarraHorizontal dados={agentes} cor="#e5533c" sufixo="vítimas" />
        </Secao>

        <Secao
          titulo="Drogas apreendidas"
          subtitulo="Peso total por ano, em toneladas"
        >
          <BarrasDrogas dados={dados.drogas} />
        </Secao>
      </div>
    </div>
  );
}

function Tile({
  icone,
  valor,
  rotulo,
}: {
  icone: React.ReactNode;
  valor: string;
  rotulo: string;
}) {
  return (
    <div className="panel rounded-xl p-4">
      <div className="flex items-center gap-1.5 text-faint">{icone}</div>
      <p className="num mt-2 text-2xl font-semibold text-ink">{valor}</p>
      <p className="mt-0.5 text-xs text-muted">{rotulo}</p>
    </div>
  );
}

function Secao({
  titulo,
  subtitulo,
  children,
}: {
  titulo: string;
  subtitulo: string;
  children: React.ReactNode;
}) {
  return (
    <section className="panel rounded-2xl p-5 sm:p-6">
      <h2 className="font-display text-xl text-ink">{titulo}</h2>
      <p className="mb-5 mt-1 text-xs text-faint">{subtitulo}</p>
      {children}
    </section>
  );
}
