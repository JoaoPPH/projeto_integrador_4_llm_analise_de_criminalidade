"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { fmt, fmtCompacto } from "@/lib/format";

interface Ponto {
  ano: number;
  total: number;
}

function Dica({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: { value: number }[];
  label?: number;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-line-2 bg-panel px-3 py-2 shadow-xl">
      <p className="text-xs text-faint">{label}</p>
      <p className="num text-beacon">{fmt(payload[0].value)}</p>
    </div>
  );
}

export default function LinhaTemporal({ dados }: { dados: Ponto[] }) {
  return (
    <div style={{ width: "100%", height: 280 }}>
      <ResponsiveContainer>
        <AreaChart data={dados} margin={{ top: 10, right: 12, bottom: 0, left: 4 }}>
          <defs>
            <linearGradient id="gradBeacon" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ffc247" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#ffc247" stopOpacity={0} />
            </linearGradient>
          </defs>
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
            tickFormatter={fmtCompacto}
          />
          <Tooltip content={<Dica />} />
          <Area
            type="monotone"
            dataKey="total"
            stroke="#ffc247"
            strokeWidth={2.5}
            fill="url(#gradBeacon)"
            dot={{ r: 3, fill: "#ffc247", strokeWidth: 0 }}
            activeDot={{ r: 5 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
