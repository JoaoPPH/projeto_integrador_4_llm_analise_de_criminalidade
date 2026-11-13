import type { NextConfig } from "next";
import path from "node:path";

// Em desenvolvimento (next dev) o Next encaminha /api/* para a API Python.
// Na exportação estática (NEXT_EXPORT=1) as páginas são servidas pelo próprio
// FastAPI, então as chamadas relativas /api/* já caem na mesma origem.
const API_URL = (process.env.API_URL || "http://127.0.0.1:8000").replace(
  /\/+$/,
  ""
);
const exportando = process.env.NEXT_EXPORT === "1";

const nextConfig: NextConfig = {
  // Não gera AGENTS.md automaticamente no `next dev`.
  agentRules: false,
  ...(exportando
    ? { output: "export" as const, trailingSlash: true }
    : {
        async rewrites() {
          return {
            beforeFiles: [
              {
                source: "/api/:path*",
                destination: `${API_URL}/api/:path*`,
              },
            ],
          };
        },
      }),
  turbopack: {
    root: path.resolve(process.cwd()),
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
