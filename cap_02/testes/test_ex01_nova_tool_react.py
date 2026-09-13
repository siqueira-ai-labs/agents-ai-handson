"""
Testes unitários — Ex01: Nova Tool no ReAct (calculator + Tavily)
"""
import os
import sys
import pathlib
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


# ── Fixture de importação com mocks ──────────────────────────────────────────

@pytest.fixture(scope="module")
def ex01():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="√144 × 7 = 84.")
    mock_llm.bind_tools.return_value = mock_llm

    # TavilySearchResults não faz chamadas de rede no __init__, só precisa da key
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test", "TAVILY_API_KEY": "tvly-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex01_nova_tool_react_solucao as mod
            mod.llm = mock_llm
            mod.llm_with_tools = mock_llm
            yield mod


# ── Testes: ferramenta calculator ─────────────────────────────────────────────

def test_calculator_soma(ex01):
    assert ex01.calculator.invoke({"expression": "2 + 2"}) == "4"


def test_calculator_multiplicacao(ex01):
    assert ex01.calculator.invoke({"expression": "12 * 7"}) == "84"


def test_calculator_raiz(ex01):
    assert ex01.calculator.invoke({"expression": "144 ** 0.5"}) == "12.0"


def test_calculator_expressao_composta(ex01):
    assert ex01.calculator.invoke({"expression": "(10 + 5) * 2"}) == "30"


def test_calculator_erro_retorna_string(ex01):
    resultado = ex01.calculator.invoke({"expression": "abc + xyz"})
    assert isinstance(resultado, str)
    assert "Erro" in resultado or len(resultado) > 0


def test_calculator_nao_levanta_excecao(ex01):
    resultado = ex01.calculator.invoke({"expression": "__import__('os').system('echo x')"})
    assert isinstance(resultado, str)


def test_calculator_divisao(ex01):
    resultado = float(ex01.calculator.invoke({"expression": "10 / 4"}))
    assert abs(resultado - 2.5) < 1e-9


# ── Testes: estrutura do grafo ────────────────────────────────────────────────

def test_build_react_graph_retorna_grafo(ex01):
    app = ex01.build_react_graph()
    assert app is not None


def test_grafo_tem_no_agent(ex01):
    app = ex01.build_react_graph()
    nodes = list(app.nodes)
    assert "agent" in nodes


def test_grafo_tem_no_tools(ex01):
    app = ex01.build_react_graph()
    nodes = list(app.nodes)
    assert "tools" in nodes


def test_tools_tem_dois_itens(ex01):
    assert len(ex01.tools) == 2


def test_agent_node_retorna_messages(ex01):
    ex01.llm_with_tools.invoke.return_value = AIMessage(content="Resposta de teste")
    state = {"messages": [HumanMessage(content="Olá")]}
    result = ex01.agent_node(state)
    assert "messages" in result
    assert len(result["messages"]) == 1
