"""Testes unitários — Ex02: Validação Estruturada com Pydantic"""
import os
import sys
import pathlib
from unittest.mock import MagicMock, patch
import pytest
from pydantic import ValidationError

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))


@pytest.fixture(scope="module")
def ex02():
    email_obj = MagicMock(assunto_email="Teste", corpo_email="Corpo", nivel_agressividade_venda=3)
    mock_structured = MagicMock()
    mock_structured.return_value = email_obj   # chamado como função pelo LCEL
    mock_structured.invoke.return_value = email_obj
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex02_validacao_pydantic_solucao as mod
            yield mod


def test_email_schema_campos_obrigatorios(ex02):
    from ex02_validacao_pydantic_solucao import EmailSchema
    obj = EmailSchema(assunto_email="A", corpo_email="B", nivel_agressividade_venda=3)
    assert obj.assunto_email == "A"
    assert obj.corpo_email == "B"
    assert obj.nivel_agressividade_venda == 3


def test_email_schema_nivel_minimo(ex02):
    from ex02_validacao_pydantic_solucao import EmailSchema
    obj = EmailSchema(assunto_email="A", corpo_email="B", nivel_agressividade_venda=1)
    assert obj.nivel_agressividade_venda == 1


def test_email_schema_nivel_maximo(ex02):
    from ex02_validacao_pydantic_solucao import EmailSchema
    obj = EmailSchema(assunto_email="A", corpo_email="B", nivel_agressividade_venda=5)
    assert obj.nivel_agressividade_venda == 5


def test_email_schema_rejeita_nivel_zero(ex02):
    from ex02_validacao_pydantic_solucao import EmailSchema
    with pytest.raises(ValidationError):
        EmailSchema(assunto_email="A", corpo_email="B", nivel_agressividade_venda=0)


def test_email_schema_rejeita_nivel_seis(ex02):
    from ex02_validacao_pydantic_solucao import EmailSchema
    with pytest.raises(ValidationError):
        EmailSchema(assunto_email="A", corpo_email="B", nivel_agressividade_venda=6)


def test_pipeline_retorna_objeto(ex02):
    result = ex02.pipeline.invoke({"produto": "software X"})
    assert result is not None


def test_with_structured_output_e_chamado(ex02):
    ex02.llm.with_structured_output.assert_called()
