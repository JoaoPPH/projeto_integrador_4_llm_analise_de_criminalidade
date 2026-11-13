"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { fmt } from "@/lib/format";

export interface FatiaRosca {
  nome: string;
  valor: number;
  cor: string;
}

function Dica({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: FatiaRosca }[];
}) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-line-2 bg-panel px-3 py-2 shadow-xl">
      <p className="text-sm text-ink">{d.nome}</p>
      <p className="num" style={{ color: d.cor }}>
        {fmt(d.valor)}
      </p>
    </div>
  );
}

export default function Rosca({ dados }: { dados: FatiaRosca[] }) {
  const total = dados.reduce((s, d) => s + d.valor, 0);
  return (
    <div className="flex flex-col items-center gap-5 sm:flex-row">
      <div style={{ width: 190, height: 190 }} className="relative shrink-0">
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={dados}
              dataKey="valor"
              nameKey="nome"
              innerRadius={58}
              outerRadius={88}
              paddingAngle={2}
              stroke="none"
            >
              {dados.map((d, i) => (
                <Cell key={i} fill={d.cor} />
              ))}
            </Pie>
            <Tooltip content={<Dica />} />
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="num text-xl font-semibold text-ink">
            {fmt(total)}
          </span>
          <span className="text-[0.68rem] text-faint">vítimas</span>
        </div>
      </div>
      <ul className="w-full space-y-2.5">
        {dados.map((d) => {
          const pct = total > 0 ? (d.valor / total) * 100 : 0;
          return (
            <li key={d.nome} className="flex items-center gap-3 text-sm">
              <span
                className="h-2.5 w-2.5 shrink-0 rounded-full"
                style={{ background: d.cor }}
              />
              <span className="flex-1 text-muted">{d.nome}</span>
              <span className="num text-ink">{fmt(d.valor)}</span>
              <span className="num w-14 text-right text-faint">
                {pct.toFixed(1)}%
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
