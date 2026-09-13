"""Testes unitários — Ex03: Orquestração com Fallback"""
import pathlib
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex03_orquestracao_fallback_solucao as ex03


@pytest.fixture(autouse=True)
def reset_stats():
    ex03.stats["langflow"] = 0
    ex03.stats["fallback"] = 0
    yield


def test_usa_langflow_quando_saudavel_e_bem_sucedido():
    with patch.object(ex03, "is_langflow_healthy", return_value=True), \
         patch.object(ex03, "run_flow", return_value={"outputs": "resposta langflow"}):
        resposta, provider = ex03.run_with_fallback("pergunta")
    assert provider == "langflow"
    assert ex03.stats["langflow"] == 1
    assert ex03.stats["fallback"] == 0


def test_usa_fallback_quando_langflow_nao_saudavel():
    with patch.object(ex03, "is_langflow_healthy", return_value=False), \
         patch.object(ex03, "_run_langchain_fallback", return_value="resposta fallback"):
        resposta, provider = ex03.run_with_fallback("pergunta")
    assert provider == "langchain-fallback"
    assert resposta == "resposta fallback"
    assert ex03.stats["fallback"] == 1
    assert ex03.stats["langflow"] == 0


def test_usa_fallback_quando_langflow_saudavel_mas_falha():
    with patch.object(ex03, "is_langflow_healthy", return_value=True), \
         patch.object(ex03, "run_flow", side_effect=TimeoutError("timeout")), \
         patch.object(ex03, "_run_langchain_fallback", return_value="resposta fallback"):
        resposta, provider = ex03.run_with_fallback("pergunta")
    assert provider == "langchain-fallback"
    assert ex03.stats["fallback"] == 1
    assert ex03.stats["langflow"] == 0


def test_fallback_tambem_falha_retorna_mensagem_de_erro():
    with patch.object(ex03, "is_langflow_healthy", return_value=False), \
         patch.object(ex03, "_run_langchain_fallback", side_effect=RuntimeError("boom")):
        resposta, provider = ex03.run_with_fallback("pergunta")
    assert provider == "langchain-fallback"
    assert "boom" in resposta
