"""Testes unitários — Ex03: Enriquecimento de Contexto com RunnableLambda"""
import os
import sys
import json
import pathlib
import tempfile
from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))


@pytest.fixture(scope="module")
def ex03():
    mock_llm = MagicMock()
    mock_llm.return_value = AIMessage(content="def timeit(func): ...")
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex03_enriquecimento_contexto_solucao as mod
            yield mod


def test_knowledge_base_carregada(ex03):
    assert len(ex03._KNOWLEDGE_BASE) >= 5


def test_knowledge_base_tem_campos(ex03):
    for entry in ex03._KNOWLEDGE_BASE:
        assert "tarefa" in entry
        assert "codigo" in entry


def test_enrich_context_retorna_dict(ex03):
    result = ex03.enrich_context("criar um decorator de tempo")
    assert isinstance(result, dict)
    assert "task" in result
    assert "examples" in result


def test_enrich_context_preserva_task(ex03):
    task = "ordenar lista por chave"
    result = ex03.enrich_context(task)
    assert result["task"] == task


def test_enrich_context_exemplos_nao_vazios(ex03):
    result = ex03.enrich_context("fibonacci com memoização")
    assert result["examples"].strip() != ""


def test_enrich_context_retorna_dois_exemplos(ex03):
    result = ex03.enrich_context("gerenciador de contexto para banco")
    assert result["examples"].count("Exemplo") == 2


def test_pipeline_invocavel(ex03):
    result = ex03.pipeline.invoke("medir tempo de execução")
    assert isinstance(result, str)


def test_pipeline_sem_enriquecimento_existe(ex03):
    assert hasattr(ex03, "pipeline_sem_enriquecimento")
