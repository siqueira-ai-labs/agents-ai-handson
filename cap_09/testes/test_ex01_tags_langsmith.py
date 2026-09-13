"""Testes unitários — Ex01: Tags no LangSmith"""
import os
import pathlib
import sys
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))


@pytest.fixture(scope="module")
def ex01():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="Resposta de teste", tool_calls=[])
    mock_llm.bind_tools.return_value = mock_llm

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test", "LANGFUSE_PUBLIC_KEY": "pk-test", "LANGFUSE_SECRET_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex01_tags_langsmith_solucao as mod
            yield mod


def test_modulo_importavel(ex01):
    assert ex01 is not None


def test_config_tem_tags_e_metadata(ex01):
    assert ex01.config["tags"] == ["cap_09", "finance-agent", "production"]
    assert ex01.config["metadata"] == {"user_id": "test-user", "session_id": "abc123"}
    assert ex01.config["run_name"] == "finance-agent-cap09"


def test_langchain_project_configurado(ex01):
    assert os.environ.get("LANGCHAIN_PROJECT") == "agents-ai-handson-cap09"


def test_run_with_tags_invoca_app_com_config(ex01):
    fake_state = {"messages": [AIMessage(content="ok")]}
    with patch.object(ex01.app, "invoke", return_value=fake_state) as mock_invoke:
        resultado = ex01.run_with_tags("pergunta de teste")
    assert resultado == "ok"
    _, kwargs = mock_invoke.call_args
    assert kwargs["config"] is ex01.config
