
import pytest
from services.n8n_client import analisar_criminalidade
from unittest.mock import patch


def test_uf_obrigatoria():
    with pytest.raises(ValueError, match="Informe a UF"):
        analisar_criminalidade(
            uf="",
            municipio="Vitória"
        )

def test_municipio_obrigatorio():
    with pytest.raises(ValueError, match="Informe o município"):
        analisar_criminalidade(
            uf="ES",
            municipio=""
        )

def test_resposta_sucesso_n8n():
    resposta_simulada = {
        "success": True,
        "analise": "Recomendações de segurança para Vitória."
    }

    with patch("services.n8n_client.requests.post") as mock_post:
        mock_post.return_value.json.return_value = resposta_simulada

        resultado = analisar_criminalidade(
            uf="ES",
            municipio="Vitória"
        )

        assert resultado == resposta_simulada
        mock_post.assert_called_once()