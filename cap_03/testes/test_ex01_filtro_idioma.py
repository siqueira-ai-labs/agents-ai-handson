"""Testes unitários — Ex01: Filtro de Idioma (LCEL)"""
import os
import sys
import pathlib
from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))


@pytest.fixture(scope="module")
def ex01():
    mock_llm = MagicMock()
    # LCEL coerce_to_runnable envolve callables em RunnableLambda → chama mock_llm(input)
    mock_llm.return_value = AIMessage(content="def sort_dicts(): pass")
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex01_filtro_idioma_solucao as mod
            yield mod


def test_pipeline_existe(ex01):
    assert hasattr(ex01, "pipeline")


def test_pipeline_invocavel(ex01):
    result = ex01.pipeline.invoke({"task": "ordenar lista", "idioma": "inglês"})
    assert isinstance(result, str)


def test_pipeline_aceita_idioma_portugues(ex01):
    result = ex01.pipeline.invoke({"task": "ordenar lista", "idioma": "português"})
    assert isinstance(result, str)


def test_prompt_contem_variavel_idioma(ex01):
    template_str = str(ex01.generation_prompt)
    assert "idioma" in template_str


def test_prompt_contem_variavel_task(ex01):
    template_str = str(ex01.generation_prompt)
    assert "task" in template_str


def test_llm_e_chamado_na_invocacao(ex01):
    import ex01_filtro_idioma_solucao as mod
    mod.llm.reset_mock()
    ex01.pipeline.invoke({"task": "teste", "idioma": "inglês"})
    assert mod.llm.called
