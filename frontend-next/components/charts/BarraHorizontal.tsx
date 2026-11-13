"use client";

import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fmt, fmtCompacto } from "@/lib/format";

export interface ItemBarra {
  nome: string;
  valor: number;
}

interface Props {
  dados: ItemBarra[];
  cor?: string;
  gradiente?: boolean;
  altura?: number;
  sufixo?: string;
}

const ESCALA = ["#e5533c", "#ef7e3b", "#f0a830", "#53c4e8", "#3fb68b"];

function Dica({
  active,
  payload,
  sufixo,
}: {
  active?: boolean;
  payload?: { payload: ItemBarra }[];
  sufixo?: string;
}) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-line-2 bg-panel px-3 py-2 shadow-xl">
      <p className="max-w-[220px] text-sm text-ink">{d.nome}</p>
      <p className="num mt-0.5 text-beacon">
        {fmt(d.valor)}
        {sufixo ? ` ${sufixo}` : ""}
      </p>
    </div>
  );
}

export default function BarraHorizontal({
  dados,
  cor = "#ffc247",
  gradiente,
  altura,
  sufixo,
}: Props) {
  const h = altura ?? Math.max(dados.length * 42 + 20, 120);
  return (
    <div style={{ width: "100%", height: h }}>
      <ResponsiveContainer>
        <BarChart
          data={dados}
          layout="vertical"
          margin={{ top: 4, right: 56, bottom: 4, left: 8 }}
          barCategoryGap={9}
        >
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="nome"
            width={158}
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#96a6c0", fontSize: 12.5 }}
            tickFormatter={(v: string) =>
              v.length > 22 ? `${v.slice(0, 21)}…` : v
            }
          />
          <Tooltip
            cursor={{ fill: "rgba(148,163,184,0.08)" }}
            content={<Dica sufixo={sufixo} />}
          />
          <Bar
            dataKey="valor"
            radius={[0, 5, 5, 0]}
            label={{
              position: "right",
              fill: "#96a6c0",
              fontSize: 11.5,
              formatter: (v: unknown) => fmtCompacto(Number(v)),
            }}
          >
            {dados.map((_, i) => (
              <Cell
                key={i}
                fill={gradiente ? ESCALA[i % ESCALA.length] : cor}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
