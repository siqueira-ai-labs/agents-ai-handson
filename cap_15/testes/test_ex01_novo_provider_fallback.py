"""Testes unitários — Ex01: Fallback de Provider"""
import os
import pathlib
import sys
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

os.environ.setdefault("OPENROUTER_API_KEY", "sk-test")

import ex01_novo_provider_fallback_solucao as ex01


def test_modulo_importavel():
    assert ex01 is not None


def test_invoke_with_fallback_usa_primario_quando_disponivel():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="resposta primária")
    with patch.object(ex01, "make_primary_llm", return_value=mock_llm):
        resposta, provider = ex01.invoke_with_fallback("pergunta")
    assert provider == "primary"
    assert resposta == "resposta primária"


def test_invoke_with_fallback_usa_fallback_quando_primario_falha():
    mock_primary = MagicMock()
    mock_primary.invoke.side_effect = Exception("rate limited")
    mock_fallback = MagicMock()
    mock_fallback.invoke.return_value = AIMessage(content="resposta fallback")
    with patch.object(ex01, "make_primary_llm", return_value=mock_primary), \
         patch.object(ex01, "make_fallback_llm", return_value=mock_fallback):
        resposta, provider = ex01.invoke_with_fallback("pergunta")
    assert provider == "fallback"
    assert resposta == "resposta fallback"


def test_invoke_with_fallback_retorna_none_quando_ambos_falham():
    mock_primary = MagicMock()
    mock_primary.invoke.side_effect = Exception("falhou")
    mock_fallback = MagicMock()
    mock_fallback.invoke.side_effect = Exception("falhou também")
    with patch.object(ex01, "make_primary_llm", return_value=mock_primary), \
         patch.object(ex01, "make_fallback_llm", return_value=mock_fallback):
        resposta, provider = ex01.invoke_with_fallback("pergunta")
    assert provider == "none"


def test_health_check_reporta_status_dos_dois_providers():
    mock_ok = MagicMock()
    mock_ok.invoke.return_value = AIMessage(content="pong")
    mock_fail = MagicMock()
    mock_fail.invoke.side_effect = Exception("indisponível")
    with patch.object(ex01, "make_primary_llm", return_value=mock_ok), \
         patch.object(ex01, "make_fallback_llm", return_value=mock_fail):
        status = ex01.health_check()
    assert status == {"primary": True, "fallback": False}
