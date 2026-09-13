"""Testes unitários — Ex01: Nova Fonte de Dados"""
import os
import sys
import pathlib
import json
from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))


@pytest.fixture(scope="module")
def ex01():
    mock_llm = MagicMock()
    mock_llm.return_value = AIMessage(content="Resposta mock", tool_calls=[])
    mock_llm.bind_tools.return_value = mock_llm

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex01_nova_fonte_dados_solucao as mod
            yield mod


def test_vendas_csv_existe(ex01):
    assert ex01.VENDAS_PATH.exists()


def test_produtos_csv_existe(ex01):
    assert ex01.PRODUTOS_PATH.exists()


def test_devolucoes_json_existe(ex01):
    assert ex01.DEVOLUCOES_PATH.exists()


def test_devolucoes_tem_10_ou_mais_registros(ex01):
    with open(ex01.DEVOLUCOES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) >= 10


def test_tools_definidas(ex01):
    assert hasattr(ex01, "tools")
    assert len(ex01.tools) >= 3


def test_consultar_vendas_existe(ex01):
    assert hasattr(ex01, "consultar_vendas")


def test_consultar_produtos_existe(ex01):
    assert hasattr(ex01, "consultar_produtos")


def test_consultar_devolucoes_existe(ex01):
    assert hasattr(ex01, "consultar_devolucoes")


def test_app_compilado(ex01):
    assert ex01.app is not None


def test_run_query_retorna_str(ex01):
    resp_msg = AIMessage(content="Headset Gamer tem a maior taxa de devolução", tool_calls=[])
    mock_state = {"messages": [resp_msg]}
    with patch.object(ex01.app, "invoke", return_value=mock_state):
        result = ex01.run_query("Qual produto tem mais devoluções?")
    assert isinstance(result, str)
    assert len(result) > 0
