"""
Testes unitários — Ex03: Configuração VCR.py e comportamento do agente

Não faz chamadas reais à API — testa a configuração do VCR e o
comportamento do agente com HTTP interceptado pelo unittest.mock.
"""
import os
import pathlib
from unittest.mock import MagicMock, patch

import pytest
import vcr
from langchain_core.messages import AIMessage, HumanMessage


# ── Fixture de importação (reutiliza ex01 que ex03 também usa) ────────────────

@pytest.fixture(scope="module")
def ex01():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="84")
    mock_llm.bind_tools.return_value = mock_llm

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test", "TAVILY_API_KEY": "tvly-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex01_nova_tool_react_solucao as mod
            mod.llm = mock_llm
            mod.llm_with_tools = mock_llm
            yield mod


# ── Testes: diretório de cassetes ─────────────────────────────────────────────

def test_cassettes_dir_existe():
    cassettes_dir = pathlib.Path(__file__).parent.parent / "cassettes"
    assert cassettes_dir.exists(), f"Diretório de cassetes não existe: {cassettes_dir}"


def test_cassettes_dir_e_diretorio():
    cassettes_dir = pathlib.Path(__file__).parent.parent / "cassettes"
    assert cassettes_dir.is_dir()


# ── Testes: configuração do VCR ───────────────────────────────────────────────

def test_vcr_pode_ser_instanciado():
    cassettes_dir = str(pathlib.Path(__file__).parent.parent / "cassettes")
    my_vcr = vcr.VCR(
        cassette_library_dir=cassettes_dir,
        record_mode="none",
        filter_headers=["authorization", "x-api-key"],
    )
    assert my_vcr is not None


def test_vcr_filtro_de_headers():
    cassettes_dir = str(pathlib.Path(__file__).parent.parent / "cassettes")
    my_vcr = vcr.VCR(
        cassette_library_dir=cassettes_dir,
        record_mode="none",
        filter_headers=["authorization", "x-api-key"],
    )
    assert "authorization" in my_vcr.filter_headers
    assert "x-api-key" in my_vcr.filter_headers


def test_vcr_cassette_library_dir():
    cassettes_dir = str(pathlib.Path(__file__).parent.parent / "cassettes")
    my_vcr = vcr.VCR(cassette_library_dir=cassettes_dir, record_mode="none")
    assert my_vcr.cassette_library_dir == cassettes_dir


# ── Testes: comportamento do agente (sem HTTP real) ───────────────────────────

def test_agent_retorna_ai_message(ex01, mocker):
    # mocker é function-scoped: restaura o return_value após o teste
    mocker.patch.object(
        ex01.llm_with_tools, "invoke",
        return_value=AIMessage(content="Resposta direta sem tools.")
    )
    app = ex01.build_react_graph()

    result = app.invoke({"messages": [HumanMessage(content="Olá, quem é você?")]})
    last = result["messages"][-1]
    assert isinstance(last, AIMessage)


def test_agent_propaga_mensagem_humana(ex01):
    app = ex01.build_react_graph()

    result = app.invoke({"messages": [("human", "Pergunta de teste")]})
    assert len(result["messages"]) >= 1


def test_calculator_no_agent_retorna_84(ex01):
    resultado = ex01.calculator.invoke({"expression": "12 * 7"})
    assert resultado == "84"
