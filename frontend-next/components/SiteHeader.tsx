"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

/** Marca própria: um sinal de varredura (arcos concêntricos), coerente com o
 *  radar de carregamento — não um ícone de biblioteca dentro de uma caixinha. */
function MarcaSinal() {
  return (
    <svg
      width="30"
      height="30"
      viewBox="0 0 28 28"
      fill="none"
      className="shrink-0"
      aria-hidden
    >
      <circle cx="7" cy="21" r="2.6" fill="var(--color-beacon)" />
      <path
        d="M7 14 A7 7 0 0 1 14 21"
        stroke="var(--color-beacon)"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.95"
      />
      <path
        d="M7 10 A11 11 0 0 1 18 21"
        stroke="var(--color-beacon)"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.55"
      />
      <path
        d="M7 6 A15 15 0 0 1 22 21"
        stroke="var(--color-beacon)"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.28"
      />
    </svg>
  );
}

const LINKS = [
  { href: "/", rotulo: "Consulta" },
  { href: "/panorama", rotulo: "Panorama" },
];

export default function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-20 bg-canvas/70 backdrop-blur-sm">
      <div className="mx-auto flex h-[4.5rem] max-w-6xl items-center justify-between px-5">
        <Link
          href="/"
          className="group flex items-baseline gap-2.5"
          aria-label="Rota Segura — início"
        >
          <span className="self-center transition-transform duration-500 group-hover:-rotate-6">
            <MarcaSinal />
          </span>
          <span className="font-display text-[1.35rem] font-medium leading-none tracking-tight text-ink">
            Rota Segura
          </span>
        </Link>

        <nav className="flex items-center gap-7">
          {LINKS.map((l) => {
            const ativo = pathname === l.href;
            return (
              <Link
                key={l.href}
                href={l.href}
                aria-current={ativo ? "page" : undefined}
                className="group relative flex items-center gap-2 py-1 text-[0.95rem]"
              >
                <span
                  className={`h-1.5 w-1.5 rounded-full transition-all ${
                    ativo
                      ? "bg-beacon shadow-[0_0_8px_var(--color-beacon)]"
                      : "bg-transparent"
                  }`}
                  aria-hidden
                />
                <span
                  className={
                    ativo
                      ? "text-ink"
                      : "text-muted transition-colors group-hover:text-ink"
                  }
                >
                  {l.rotulo}
                </span>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Linha-rota: a base do cabeçalho é um traçado de rota, não uma régua comum. */}
      <div
        className="h-px w-full"
        style={{
          backgroundImage:
            "repeating-linear-gradient(to right, rgba(255,194,71,0.45) 0 9px, transparent 9px 20px)",
        }}
      />
    </header>
  );
}
