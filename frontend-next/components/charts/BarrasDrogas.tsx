"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fmt1 } from "@/lib/format";

interface Ponto {
  ano: number;
  cocaina: number;
  maconha: number;
}

function Dica({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: number;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-line-2 bg-panel px-3 py-2 shadow-xl">
      <p className="mb-1 text-xs text-faint">{label}</p>
      {payload.map((p) => (
        <p key={p.name} className="num text-sm" style={{ color: p.color }}>
          {p.name}: {fmt1(p.value)} t
        </p>
      ))}
    </div>
  );
}

export default function BarrasDrogas({ dados }: { dados: Ponto[] }) {
  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <BarChart data={dados} margin={{ top: 8, right: 12, bottom: 0, left: 4 }}>
          <CartesianGrid stroke="#243149" vertical={false} />
          <XAxis
            dataKey="ano"
            tickLine={false}
            axisLine={{ stroke: "#243149" }}
            tick={{ fill: "#96a6c0", fontSize: 12 }}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            width={46}
            tick={{ fill: "#96a6c0", fontSize: 12 }}
            tickFormatter={(v: number) => `${v} t`}
          />
          <Tooltip cursor={{ fill: "rgba(148,163,184,0.08)" }} content={<Dica />} />
          <Legend
            iconType="circle"
            wrapperStyle={{ fontSize: 13, color: "#96a6c0", paddingTop: 8 }}
          />
          <Bar dataKey="cocaina" name="Cocaína" fill="#53c4e8" radius={[4, 4, 0, 0]} />
          <Bar dataKey="maconha" name="Maconha" fill="#3fb68b" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
