import os

import requests


N8N_BASE_URL = os.getenv(
    "N8N_BASE_URL",
    "http://107.175.155.135:5678",
).rstrip("/")

TIMEOUT = 70


class N8NError(Exception):
    """Erro de comunicação com o workflow do n8n."""


def analisar_criminalidade(
    uf: str,
    municipio: str,
    meio_transporte: str = "Não informado",
    acompanhantes: str = "Não informado",
    periodo: str = "Não informado",
    objetivo: str = "Não informado",
) -> dict:
    """Envia o contexto do usuário e retorna a análise da IA."""

    if not uf or not uf.strip():
        raise ValueError("Informe a UF.")

    if not municipio or not municipio.strip():
        raise ValueError("Informe o município.")

    url = f"{N8N_BASE_URL}/webhook/criminalidade/analise-llm"

    payload = {
        "uf": uf.strip().upper(),
        "municipio": municipio.strip(),
        "meio_transporte": meio_transporte,
        "acompanhantes": acompanhantes,
        "periodo": periodo,
        "objetivo": objetivo,
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=TIMEOUT,
        )
        response.raise_for_status()

    except requests.Timeout as exc:
        raise N8NError(
            "O n8n demorou demais para responder."
        ) from exc

    except requests.RequestException as exc:
        raise N8NError(
            "Não foi possível comunicar com o n8n."
        ) from exc

    try:
        resultado = response.json()
    except ValueError as exc:
        raise N8NError(
            "O n8n retornou uma resposta que não é JSON válido."
        ) from exc

    if not isinstance(resultado, dict):
        raise N8NError("Formato de resposta inesperado do n8n.")

    if not resultado.get("success", False):
        mensagem = resultado.get("error", "Erro na análise.")
        raise N8NError(str(mensagem))

    if not resultado.get("analise"):
        raise N8NError("A resposta não contém a análise da IA.")

    return resultado
