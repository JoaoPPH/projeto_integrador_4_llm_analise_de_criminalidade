export default function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-line/70">
      <div className="mx-auto max-w-6xl px-5 py-10">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
          <div className="max-w-md">
            <p className="font-display text-base text-ink">Rota Segura</p>
            <p className="mt-2 text-sm leading-relaxed text-muted">
              Leitura de segurança por destino, construída sobre a base pública
              de ocorrências de criminalidade do Brasil e interpretada por um
              modelo de linguagem.
            </p>
          </div>
          <div className="text-sm text-faint">
            <p>Projeto Integrador 4</p>
            <p className="mt-1">Dados oficiais · análise por IA</p>
          </div>
        </div>
        <p className="mt-8 text-xs leading-relaxed text-faint">
          As recomendações são orientativas e derivam de dados históricos. Elas
          não substituem o bom senso nem as orientações das autoridades de
          segurança locais.
        </p>
      </div>
    </footer>
  );
}
