"""Testes unitários — Ex02: Hibridização RAG como Fallback"""
import os
import pathlib
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))

os.environ.setdefault("OPENAI_API_KEY", "sk-test")

import ex02_hibridizacao_rag_fallback_solucao as ex02


def _fake_response(logprobs, content="resposta do modelo"):
    tokens = [SimpleNamespace(logprob=lp) for lp in logprobs]
    choice = SimpleNamespace(
        logprobs=SimpleNamespace(content=tokens),
        message=SimpleNamespace(content=content),
    )
    return SimpleNamespace(choices=[choice])


def test_modulo_importavel():
    assert ex02 is not None


def test_get_model_confidence_alta_para_logprobs_proximos_de_zero():
    resp = _fake_response([-0.01, -0.02, -0.01])
    assert ex02.get_model_confidence(resp) > 0.95


def test_get_model_confidence_baixa_para_logprobs_negativos():
    resp = _fake_response([-2.0, -3.0, -2.5])
    assert ex02.get_model_confidence(resp) < 0.2


def test_get_model_confidence_sem_logprobs_retorna_zero():
    resp = SimpleNamespace(choices=[SimpleNamespace(logprobs=None)])
    assert ex02.get_model_confidence(resp) == 0.0


def test_hybrid_query_usa_fine_tuned_quando_confianca_alta():
    resp = _fake_response([-0.01, -0.01], content="resposta confiante")
    with patch.object(ex02, "query_finetuned", return_value=resp):
        resposta, fonte = ex02.hybrid_query("pergunta", threshold=0.7)
    assert fonte == "fine-tuned"
    assert resposta == "resposta confiante"


def test_hybrid_query_usa_rag_quando_confianca_baixa():
    resp = _fake_response([-3.0, -3.0], content="resposta incerta")
    fake_chain = object()
    with patch.object(ex02, "query_finetuned", return_value=resp), \
         patch.object(ex02, "rag_answer", return_value="resposta do RAG") as mock_rag:
        resposta, fonte = ex02.hybrid_query("pergunta", threshold=0.7, rag_chain=fake_chain)
    assert fonte == "rag-fallback"
    assert resposta == "resposta do RAG"
    mock_rag.assert_called_once_with("pergunta", chain=fake_chain)
