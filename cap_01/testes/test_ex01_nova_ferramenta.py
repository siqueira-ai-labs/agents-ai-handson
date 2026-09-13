"""
Testes unitários — Ex01: Adicionando uma Nova Ferramenta
"""
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# ── Fixtures de importação ─────────────────────────────────────────────────────
# O módulo inicializa LLM e tools no nível de módulo; mockamos antes de importar.

@pytest.fixture(scope="module")
def ex01():
    mocks = {
        "OPENROUTER_API_KEY": "test-key",
        "TAVILY_API_KEY": "test-key",
    }
    with patch.dict(os.environ, mocks):
        with patch("langchain_openai.ChatOpenAI", return_value=MagicMock()):
            with patch(
                "langchain_community.tools.tavily_search.TavilySearchResults",
                return_value=MagicMock(name="tavily"),
            ):
                with patch("langchain.agents.create_tool_calling_agent", return_value=MagicMock()):
                    with patch("langchain.agents.AgentExecutor", return_value=MagicMock()):
                        sys.path.insert(0, str(
                            __file__.replace("/testes/test_ex01_nova_ferramenta.py", "/exercicios")
                        ))
                        import ex01_nova_ferramenta_solucao as mod
                        yield mod


# ── Testes da ferramenta get_current_datetime ──────────────────────────────────

def test_get_current_datetime_retorna_string(ex01):
    resultado = ex01.get_current_datetime.invoke({})
    assert isinstance(resultado, str)


def test_get_current_datetime_formato_correto(ex01):
    resultado = ex01.get_current_datetime.invoke({})
    # Deve estar no formato YYYY-MM-DD HH:MM:SS
    datetime.strptime(resultado, "%Y-%m-%d %H:%M:%S")


def test_get_current_datetime_ano_atual(ex01):
    resultado = ex01.get_current_datetime.invoke({})
    ano = int(resultado[:4])
    assert ano == datetime.now().year


def test_get_current_datetime_nao_retorna_vazio(ex01):
    resultado = ex01.get_current_datetime.invoke({})
    assert resultado.strip() != ""


# ── Testes de configuração do agente ──────────────────────────────────────────

def test_tools_tem_duas_ferramentas(ex01):
    assert len(ex01.tools) == 2


def test_tools_contem_busca_e_datetime(ex01):
    nomes = [getattr(t, "name", str(t)) for t in ex01.tools]
    # get_current_datetime deve estar na lista
    assert any("datetime" in str(n).lower() for n in nomes)


def test_agent_executor_configurado(ex01):
    assert ex01.agent_executor is not None
