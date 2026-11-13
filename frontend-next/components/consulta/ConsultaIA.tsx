"use client";

import { useEffect, useRef, useState } from "react";
import { ShieldCheck, Radar, AlertTriangle, Navigation } from "lucide-react";
import Combobox, { OpcaoCombo } from "@/components/Combobox";
import GrupoOpcoes from "./GrupoOpcoes";
import PainelDestino, { Estatisticas } from "./PainelDestino";
import Narrativa from "./Narrativa";
import { tituloCidade } from "@/lib/format";

const TRANSPORTES = ["Carro", "Moto", "Transporte público", "A pé", "Outro"];
const ACOMPANHANTES = ["Sozinho", "Família", "Amigos", "Outro"];
const PERIODOS = ["Manhã", "Tarde", "Noite", "Madrugada", "Vários períodos"];
const OBJETIVOS = ["Turismo", "Trabalho", "Estudo", "Moradia", "Descrever"];
const MAX_DESC = 250;

const TERMOS_COMPROMISSO =
  /\b(show|shows|concerto|festival|evento|jogo|partida|estadio|teatro|casamento|formatura|conferencia|palestra|prova|entrevista|reuniao|congresso|feira|festa|balada|aniversario|competicao|campeonato|corrida|maratona|circo|exposicao|espetaculo|apresentacao)\b/;

function normalizarTexto(texto: string): string {
  return texto.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

interface Uf {
  sigla: string;
  nome: string;
}
interface ResultadoIA {
  analise: string;
  modelo?: string;
  dados?: unknown;
  fonte?: string;
  aviso?: string;
}

type Fase = "idle" | "carregando" | "pronto";

export default function ConsultaIA() {
  const [ufs, setUfs] = useState<Uf[]>([]);
  const [municipios, setMunicipios] = useState<string[]>([]);
  const [carregandoMun, setCarregandoMun] = useState(false);

  const [uf, setUf] = useState<string | null>(null);
  const [municipio, setMunicipio] = useState<string | null>(null);

  const [transporte, setTransporte] = useState("Carro");
  const [acompanhantes, setAcompanhantes] = useState("Sozinho");
  const [periodo, setPeriodo] = useState("Noite");
  const [objetivo, setObjetivo] = useState("Turismo");
  const [objetivoLivre, setObjetivoLivre] = useState("");
  const [aceitaAlternativa, setAceitaAlternativa] = useState(false);

  const [fase, setFase] = useState<Fase>("idle");
  const [estat, setEstat] = useState<Estatisticas | null>(null);
  const [resultado, setResultado] = useState<ResultadoIA | null>(null);
  const [erroIA, setErroIA] = useState<string | null>(null);
  const [erroEstat, setErroEstat] = useState<string | null>(null);

  const refResultado = useRef<HTMLDivElement>(null);

  const descrevendo = objetivo === "Descrever";
  const objetivoEfetivo = descrevendo
    ? objetivoLivre.trim() || "Não informado"
    : objetivo;
  const descricaoPendente = descrevendo && !objetivoLivre.trim();
  const compromissoFixo = TERMOS_COMPROMISSO.test(
    normalizarTexto(objetivoEfetivo)
  );
  const aceitaEfetiva = aceitaAlternativa && !compromissoFixo;

  useEffect(() => {
    if (compromissoFixo) setAceitaAlternativa(false);
  }, [compromissoFixo]);

  useEffect(() => {
    fetch("/api/ufs")
      .then((r) => r.json())
      .then((d) => setUfs(d.ufs ?? []))
      .catch(() => setUfs([]));
  }, []);

  useEffect(() => {
    if (!uf) {
      setMunicipios([]);
      return;
    }
    setCarregandoMun(true);
    setMunicipio(null);
    fetch(`/api/municipios?uf=${encodeURIComponent(uf)}`)
      .then((r) => r.json())
      .then((d) => setMunicipios(d.municipios ?? []))
      .catch(() => setMunicipios([]))
      .finally(() => setCarregandoMun(false));
  }, [uf]);

  const opcoesUf: OpcaoCombo[] = ufs.map((u) => ({
    valor: u.sigla,
    rotulo: u.nome,
    sub: u.sigla,
  }));
  const opcoesMun: OpcaoCombo[] = municipios.map((m) => ({
    valor: m,
    rotulo: tituloCidade(m),
  }));

  async function gerar() {
    if (!uf || !municipio) return;

    setFase("carregando");
    setResultado(null);
    setEstat(null);
    setErroIA(null);
    setErroEstat(null);

    setTimeout(
      () => refResultado.current?.scrollIntoView({ behavior: "smooth", block: "start" }),
      60
    );

    const corpo = {
      uf,
      municipio,
      meio_transporte: transporte,
      acompanhantes,
      periodo,
      objetivo: objetivoEfetivo,
      aceita_alternativa: aceitaEfetiva,
    };

    const pEstat = fetch(
      `/api/estatisticas?uf=${encodeURIComponent(uf)}&municipio=${encodeURIComponent(
        municipio
      )}`
    ).then(async (r) => {
      const d = await r.json();
      if (!r.ok) throw new Error(d.error ?? "Falha nas estatísticas.");
      return d as Estatisticas;
    });

    const pIA = fetch("/api/analise", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(corpo),
    }).then(async (r) => {
      const d = await r.json();
      if (!r.ok) throw new Error(d.error ?? "Falha na análise.");
      return d as ResultadoIA;
    });

    const [rEstat, rIA] = await Promise.allSettled([pEstat, pIA]);

    if (rEstat.status === "fulfilled") setEstat(rEstat.value);
    else setErroEstat(rEstat.reason?.message ?? "Erro nas estatísticas.");

    if (rIA.status === "fulfilled") setResultado(rIA.value);
    else setErroIA(rIA.reason?.message ?? "Erro na análise.");

    setFase("pronto");
  }

  const destinoEscolhido = Boolean(uf && municipio);

  return (
    <>
      {/* ---------------- HERÓI: a pergunta + o destino ---------------- */}
      <section className="mx-auto max-w-6xl px-5 pt-16 pb-10 sm:pt-24">
        <div className="max-w-2xl">
          <p className="mb-5 inline-flex items-center gap-2 rounded-full border border-line bg-panel-2/50 px-3 py-1.5 text-xs text-muted">
            <ShieldCheck size={14} className="text-beacon" />
            Fundamentado em estatísticas oficiais de criminalidade
          </p>
          <h1 className="font-display text-5xl font-semibold leading-[1.05] tracking-tight text-ink sm:text-6xl">
            Para onde
            <br />
            você vai?
          </h1>
          <p className="mt-5 max-w-xl text-lg leading-relaxed text-muted">
            Escolha o destino e conte o contexto da viagem. A IA cruza os dados
            de ocorrências da cidade e devolve uma leitura de segurança clara,
            com recomendações e uma alternativa mais tranquila por perto.
          </p>
        </div>

        <div className="mt-10 grid gap-4 sm:max-w-2xl sm:grid-cols-2">
          <Combobox
            rotulo="Estado"
            placeholder="Selecione o estado"
            opcoes={opcoesUf}
            valor={uf}
            aoSelecionar={setUf}
          />
          <Combobox
            rotulo="Município de destino"
            placeholder={uf ? "Selecione a cidade" : "Escolha o estado antes"}
            opcoes={opcoesMun}
            valor={municipio}
            aoSelecionar={setMunicipio}
            desabilitado={!uf}
            carregando={carregandoMun}
          />
        </div>
      </section>

      {/* ---------------- CONTEXTO DA VIAGEM ---------------- */}
      {destinoEscolhido && (
        <section className="mx-auto max-w-6xl animate-rise px-5 pb-12">
          <div className="panel rounded-2xl p-6 sm:p-8">
            <h2 className="font-display text-2xl text-ink">
              Sobre a sua ida a {tituloCidade(municipio!)}
            </h2>
            <p className="mt-1 text-sm text-muted">
              Essas respostas ajustam as recomendações ao seu cenário.
            </p>

            <div className="mt-7 grid gap-7 sm:grid-cols-2">
              <GrupoOpcoes
                rotulo="Meio de transporte"
                opcoes={TRANSPORTES}
                valor={transporte}
                aoMudar={setTransporte}
              />
              <GrupoOpcoes
                rotulo="Com quem você vai"
                opcoes={ACOMPANHANTES}
                valor={acompanhantes}
                aoMudar={setAcompanhantes}
              />
              <GrupoOpcoes
                rotulo="Período"
                opcoes={PERIODOS}
                valor={periodo}
                aoMudar={setPeriodo}
              />
              <GrupoOpcoes
                rotulo="Objetivo"
                opcoes={OBJETIVOS}
                valor={objetivo}
                aoMudar={setObjetivo}
              />
            </div>

            {descrevendo && (
              <div className="mt-6 animate-rise">
                <label
                  htmlFor="objetivo-livre"
                  className="mb-2 block text-[0.82rem] font-medium text-muted"
                >
                  Descreva o objetivo da viagem
                </label>
                <textarea
                  id="objetivo-livre"
                  value={objetivoLivre}
                  onChange={(e) =>
                    setObjetivoLivre(e.target.value.slice(0, MAX_DESC))
                  }
                  maxLength={MAX_DESC}
                  rows={3}
                  placeholder="Ex.: vou a um show no centro e volto de madrugada; quero saber a que prestar atenção no trajeto."
                  className="w-full resize-none rounded-xl border border-line bg-panel-2/50 px-4 py-3 text-ink placeholder:text-faint focus:border-line-2 focus:outline-none"
                />
                <div className="mt-1.5 flex justify-end">
                  <span
                    className={`num text-xs ${
                      objetivoLivre.length >= MAX_DESC
                        ? "text-beacon"
                        : "text-faint"
                    }`}
                  >
                    {objetivoLivre.length}/{MAX_DESC}
                  </span>
                </div>
              </div>
            )}

            <div className="mt-7 flex items-start gap-3 rounded-xl border border-line bg-canvas-2/50 p-4">
              <button
                type="button"
                role="switch"
                aria-checked={aceitaEfetiva}
                disabled={compromissoFixo}
                onClick={() => setAceitaAlternativa((v) => !v)}
                className={`relative mt-0.5 h-6 w-11 shrink-0 rounded-full transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
                  aceitaEfetiva ? "bg-cyan" : "bg-line-2"
                }`}
              >
                <span
                  className={`absolute top-0.5 h-5 w-5 rounded-full bg-canvas transition-transform ${
                    aceitaEfetiva ? "translate-x-[22px]" : "translate-x-0.5"
                  }`}
                />
              </button>
              <label
                className={`text-sm leading-relaxed text-muted ${
                  compromissoFixo ? "" : "cursor-pointer"
                }`}
                onClick={() => {
                  if (!compromissoFixo) setAceitaAlternativa((v) => !v);
                }}
              >
                <span className="font-medium text-ink">
                  Aceito uma cidade alternativa mais tranquila
                </span>
                <br />
                {compromissoFixo
                  ? "Compromissos com horário fixo (show, evento, jogo) não comportam troca de cidade; a análise foca em chegada, permanência e saída."
                  : "Se marcado, a análise sugere um destino de menor incidência no mesmo estado."}
              </label>
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-4">
              <button
                type="button"
                onClick={gerar}
                disabled={fase === "carregando" || descricaoPendente}
                className="inline-flex items-center gap-2 rounded-xl bg-beacon px-6 py-3.5 font-medium text-[#1a1206] shadow-lg shadow-beacon/20 transition-all hover:bg-beacon-deep disabled:cursor-not-allowed disabled:opacity-60"
              >
                <Navigation size={18} />
                {fase === "carregando"
                  ? "Analisando o destino…"
                  : "Gerar análise de segurança"}
              </button>
              <span className="text-xs text-faint">
                {descricaoPendente
                  ? "Escreva a descrição do objetivo para continuar."
                  : "A geração pode levar alguns segundos."}
              </span>
            </div>
          </div>
        </section>
      )}

      {/* ---------------- RESULTADO ---------------- */}
      <div ref={refResultado} className="scroll-mt-20">
        {fase === "carregando" && <Carregando municipio={municipio!} />}

        {fase === "pronto" && (
          <section className="mx-auto max-w-6xl animate-rise px-5 pb-24">
            <div className="grid gap-8 lg:grid-cols-12">
              <div className="lg:col-span-7">
                {resultado ? (
                  <Narrativa
                    analise={resultado.analise}
                    modelo={resultado.modelo}
                    dados={resultado.dados}
                    fonte={resultado.fonte}
                    aviso={resultado.aviso}
                  />
                ) : (
                  <div className="rounded-2xl border border-risk-mid/35 bg-risk-mid/[0.06] p-6">
                    <div className="flex items-center gap-2 text-risk-mid">
                      <AlertTriangle size={18} />
                      <span className="font-medium">
                        A análise por IA está indisponível no momento
                      </span>
                    </div>
                    <p className="mt-2 text-sm leading-relaxed text-muted">
                      {erroIA ??
                        "Não foi possível obter a recomendação do modelo."}{" "}
                      Os dados do destino ao lado seguem disponíveis para
                      consulta.
                    </p>
                  </div>
                )}
              </div>

              <aside className="lg:col-span-5">
                {estat ? (
                  <PainelDestino
                    estat={estat}
                    mostrarAlternativa={aceitaEfetiva}
                  />
                ) : (
                  <div className="panel rounded-2xl p-6 text-sm text-muted">
                    {erroEstat ?? "Dados do destino indisponíveis."}
                  </div>
                )}
              </aside>
            </div>
          </section>
        )}
      </div>
    </>
  );
}

function Carregando({ municipio }: { municipio: string }) {
  return (
    <section className="mx-auto max-w-6xl px-5 pb-24">
      <div className="panel flex flex-col items-center justify-center rounded-2xl px-6 py-20 text-center">
        <span className="relative flex h-16 w-16 items-center justify-center">
          <span
            className="absolute inset-0 rounded-full"
            style={{
              background:
                "conic-gradient(from 0deg, transparent 0deg, rgba(255,194,71,0.55) 60deg, transparent 120deg)",
              animation: "sweep 1.4s linear infinite",
            }}
          />
          <span className="absolute inset-[3px] rounded-full bg-panel" />
          <Radar size={24} className="relative text-beacon" />
        </span>
        <p className="mt-6 font-display text-xl text-ink">
          Varrendo as ocorrências de {tituloCidade(municipio)}
        </p>
        <p className="mt-2 text-sm text-muted">
          Consultando a base e consultando o modelo de IA.
        </p>
      </div>
    </section>
  );
}
