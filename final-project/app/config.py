"""Configuração central da API, carregada do .env do projeto."""

from pathlib import Path

from dotenv import load_dotenv
import os

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
load_dotenv(RAIZ_PROJETO / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_9OVhEkPKmL0i@"
    "ep-sweet-waterfall-b5c88b0h-pooler.c-7.us-east-2.aws.neon.tech/"
    "neondb?sslmode=require",
)

LLM_API_KEY = os.getenv(
    "LLM_API_KEY",
    "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",
).strip()
LLM_BASE_URL = os.getenv(
    "LLM_BASE_URL", "https://api.groq.com/openai/v1"
).strip().rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b").strip()

LLM_TIMEOUT_S = float(os.getenv("LLM_TIMEOUT_S", "75"))

CACHE_ESTATISTICAS_S = int(os.getenv("CACHE_ESTATISTICAS_S", "900"))
CACHE_PANORAMA_S = int(os.getenv("CACHE_PANORAMA_S", "3600"))
CACHE_CATALOGO_S = int(os.getenv("CACHE_CATALOGO_S", "3600"))
CACHE_ANALISE_S = int(os.getenv("CACHE_ANALISE_S", "600"))
