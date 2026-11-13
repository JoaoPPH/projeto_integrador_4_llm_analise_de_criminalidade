"""FastAPI da aplicação."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .briefing import montar_briefing
from .catalogo import listar_municipios, listar_ufs
from .contexto import deve_sugerir_alternativa
from .db import abrir_pool, fechar_pool
from .estatisticas import obter_estatisticas
from .llm import LLMError, analisar_criminalidade, provedor_disponivel
from .markdown_render import renderizar as renderizar_markdown
from .panorama import obter_panorama
from .perfil import obter_perfil

UI_DIR = Path(__file__).resolve().parents[1] / "ui"

logger = logging.getLogger("rota_segura")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    abrir_pool()
    yield
    fechar_pool()


app = FastAPI(title="Rota Segura API", version="1.0.0", lifespan=lifespan)

def erro(status: int, mensagem: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": mensagem})


@app.exception_handler(RequestValidationError)
async def validacao_invalida(_: Request, exc: RequestValidationError):
    logger.info("Requisição inválida: %s", exc.errors())
    return erro(400, "Corpo ou parâmetros inválidos.")


@app.exception_handler(Exception)
async def erro_inesperado(_: Request, exc: Exception):
    logger.exception("Erro inesperado", exc_info=exc)
    return erro(500, "Erro interno na API.")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "ia_configurada": provedor_disponivel()}


@app.get("/api/ufs")
def ufs():
    try:
        return {"ufs": listar_ufs()}
    except Exception:
        logger.exception("Falha ao listar UFs")
        return erro(500, "Não foi possível carregar os estados.")


@app.get("/api/municipios")
def municipios(uf: str | None = Query(default=None, max_length=2)):
    sigla = (uf or "").strip().upper()
    if not sigla:
        return erro(400, "Informe a UF.")
    try:
        return {"municipios": listar_municipios(sigla)}
    except Exception:
        logger.exception("Falha ao listar municípios de %s", sigla)
        return erro(500, "Não foi possível carregar os municípios.")


@app.get("/api/estatisticas")
def estatisticas(
    uf: str | None = Query(default=None, max_length=2),
    municipio: str | None = Query(default=None, max_length=120),
):
    sigla = (uf or "").strip()
    cidade = (municipio or "").strip()
    if not sigla or not cidade:
        return erro(400, "Informe UF e município.")
    try:
        return obter_estatisticas(sigla, cidade)
    except Exception:
        logger.exception("Falha nas estatísticas de %s/%s", sigla, cidade)
        return erro(500, "Não foi possível calcular as estatísticas.")


@app.get("/api/panorama")
def panorama():
    try:
        return obter_panorama()
    except Exception:
        logger.exception("Falha ao montar o panorama")
        return erro(500, "Não foi possível carregar o panorama.")


class EntradaAnalise(BaseModel):
    """Campos livres limitados: o texto do usuário vai para o prompt da IA."""

    uf: str | None = Field(default=None, max_length=2)
    municipio: str | None = Field(default=None, max_length=120)
    meio_transporte: str = Field(default="Não informado", max_length=60)
    acompanhantes: str = Field(default="Não informado", max_length=60)
    periodo: str = Field(default="Não informado", max_length=60)
    objetivo: str = Field(default="Não informado", max_length=300)
    aceita_alternativa: bool = False


@app.post("/api/analise")
def analise(corpo: EntradaAnalise):
    uf = (corpo.uf or "").strip()
    municipio = (corpo.municipio or "").strip()
    if not uf or not municipio:
        return erro(400, "Informe UF e município.")

    contexto = {
        "uf": uf,
        "municipio": municipio,
        "meio_transporte": corpo.meio_transporte or "Não informado",
        "acompanhantes": corpo.acompanhantes or "Não informado",
        "periodo": corpo.periodo or "Não informado",
        "objetivo": corpo.objetivo or "Não informado",
        "aceita_alternativa": bool(corpo.aceita_alternativa),
    }

    try:
        estat = obter_estatisticas(uf, municipio)
    except Exception:
        logger.exception("Falha nos dados para a análise de %s/%s", uf, municipio)
        return erro(
            502,
            "Não foi possível consultar os dados do destino para a análise.",
        )

    perfil = None
    try:
        perfil = obter_perfil(uf, municipio)
    except Exception:
        logger.warning("Perfil detalhado indisponível para %s/%s", uf, municipio)

    try:
        resultado = analisar_criminalidade(estat, contexto, perfil)
        resultado["fonte"] = "ia"
        resultado["analise_html"] = renderizar_markdown(resultado.get("analise", ""))
        return resultado
    except LLMError as falha:
        logger.warning("IA indisponível (%s); usando briefing dos dados.", falha)
        analise = montar_briefing(estat, contexto, perfil)
        mostrar_alternativa = bool(
            deve_sugerir_alternativa(contexto) and estat.get("alternativa")
        )
        return {
            "analise": analise,
            "analise_html": renderizar_markdown(analise),
            "modelo": "Análise automática (dados oficiais)",
            "dados": {
                "destino": estat["destino"],
                "alternativa": (
                    estat.get("alternativa") if mostrar_alternativa else None
                ),
                "perfil": perfil or {},
            },
            "fonte": "fallback",
            "aviso": (
                f"A IA generativa está indisponível ({falha}). "
                "Esta leitura foi montada diretamente a partir dos dados."
            ),
        }


app.mount("/", StaticFiles(directory=UI_DIR, html=True), name="ui")
