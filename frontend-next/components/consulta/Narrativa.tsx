"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Sparkles, Code2, ChevronDown, Info, Database } from "lucide-react";

interface Props {
  analise: string;
  modelo?: string;
  dados?: unknown;
  fonte?: string;
  aviso?: string;
}

export default function Narrativa({ analise, modelo, dados, fonte, aviso }: Props) {
  const [verDados, setVerDados] = useState(false);
  const ehFallback = fonte === "fallback";

  return (
    <div>
      <div
        className={`mb-5 flex items-center gap-2 text-sm ${
          ehFallback ? "text-cyan" : "text-beacon"
        }`}
      >
        {ehFallback ? <Database size={16} /> : <Sparkles size={16} />}
        <span>
          {ehFallback
            ? "Leitura de segurança a partir dos dados"
            : "Recomendações personalizadas"}
        </span>
      </div>

      {aviso && (
        <div className="mb-5 flex items-start gap-2.5 rounded-xl border border-cyan/30 bg-cyan/[0.06] px-4 py-3 text-sm text-muted">
          <Info size={16} className="mt-0.5 shrink-0 text-cyan" />
          <span>{aviso}</span>
        </div>
      )}

      <div className="prose-ia">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{analise}</ReactMarkdown>
      </div>

      {dados != null && (
        <div className="mt-6 rounded-xl border border-line bg-canvas-2/50">
          <button
            type="button"
            onClick={() => setVerDados((v) => !v)}
            className="flex w-full items-center justify-between px-4 py-3 text-sm text-muted transition-colors hover:text-ink"
          >
            <span className="flex items-center gap-2">
              <Code2 size={15} />
              Dados consultados pela IA
            </span>
            <ChevronDown
              size={16}
              className={`transition-transform ${verDados ? "rotate-180" : ""}`}
            />
          </button>
          {verDados && (
            <pre className="num max-h-80 overflow-auto border-t border-line px-4 py-3 text-xs leading-relaxed text-muted">
              {JSON.stringify(dados, null, 2)}
            </pre>
          )}
        </div>
      )}

      {modelo && (
        <p className="mt-4 text-xs text-faint">
          Análise gerada pelo modelo{" "}
          <span className="text-muted">{modelo}</span>
        </p>
      )}
    </div>
  );
}
