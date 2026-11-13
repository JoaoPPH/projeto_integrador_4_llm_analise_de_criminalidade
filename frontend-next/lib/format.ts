const nf0 = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
const nf1 = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});
const nf2 = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export const fmt = (v: number) => nf0.format(v ?? 0);
export const fmt1 = (v: number) => nf1.format(v ?? 0);
export const fmt2 = (v: number) => nf2.format(v ?? 0);

/** Abrevia números grandes para rótulos de eixo (12 mil, 3,4 mi). */
export function fmtCompacto(v: number): string {
  if (Math.abs(v) >= 1_000_000) return `${nf1.format(v / 1_000_000)} mi`;
  if (Math.abs(v) >= 1_000) return `${nf0.format(v / 1_000)} mil`;
  return nf0.format(v);
}

/** Capitaliza mantendo o padrão de nomes de cidades em maiúsculas da base. */
export function tituloCidade(nome: string): string {
  if (!nome) return nome;
  if (nome === nome.toUpperCase() || nome === nome.toLowerCase()) {
    return nome
      .toLowerCase()
      .split(/(\s|-)/)
      .map((p) =>
        p.length > 2 && !["da", "de", "do", "das", "dos", "e"].includes(p)
          ? p.charAt(0).toUpperCase() + p.slice(1)
          : p
      )
      .join("");
  }
  return nome;
}
