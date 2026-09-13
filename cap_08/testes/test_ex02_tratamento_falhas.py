"""Testes unitários — Ex02: Tratamento de Falhas com TerminatedException"""
import os
import pathlib
import sys
from unittest.mock import patch

import pytest
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.replay import ReplayChatCompletionClient

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

MODEL_INFO = ModelInfo(
    vision=False,
    function_calling=False,
    json_output=False,
    family=ModelFamily.UNKNOWN,
    structured_output=False,
)


@pytest.fixture(scope="module")
def ex02():
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        import ex02_tratamento_falhas_solucao as mod
        yield mod


def test_modulo_importavel(ex02):
    assert ex02 is not None


@pytest.mark.asyncio
async def test_sucesso_na_primeira_tentativa(ex02, tmp_path, monkeypatch):
    monkeypatch.setattr(ex02, "CODING_DIR", tmp_path)
    client = ReplayChatCompletionClient(["```python\nprint(2 + 2)\n```"], model_info=MODEL_INFO)
    try:
        resultado = await ex02.run_with_retry("Calcule 2 + 2", model_client=client, max_retries=3)
    finally:
        await client.close()
    assert "4" in resultado
    assert "Falha após" not in resultado


@pytest.mark.asyncio
async def test_falha_apos_esgotar_tentativas(ex02, tmp_path, monkeypatch):
    monkeypatch.setattr(ex02, "CODING_DIR", tmp_path)
    replies = ["```python\nprint(1 / 0)\n```"] * 3
    client = ReplayChatCompletionClient(replies, model_info=MODEL_INFO)
    try:
        resultado = await ex02.run_with_retry("Calcule 1 / 0", model_client=client, max_retries=3)
    finally:
        await client.close()
    assert "Falha após 3 tentativas" in resultado


@pytest.mark.asyncio
async def test_registra_cada_tentativa_no_log(ex02, tmp_path, monkeypatch):
    monkeypatch.setattr(ex02, "CODING_DIR", tmp_path)
    log_path = tmp_path / "execution.log"
    monkeypatch.setattr(ex02, "LOG_PATH", log_path)
    for h in list(ex02.logger.handlers):
        ex02.logger.removeHandler(h)
    import logging
    handler = logging.FileHandler(str(log_path))
    ex02.logger.addHandler(handler)

    client = ReplayChatCompletionClient(["```python\nprint(1 / 0)\n```"] * 2, model_info=MODEL_INFO)
    try:
        await ex02.run_with_retry("Calcule 1 / 0", model_client=client, max_retries=2)
    finally:
        await client.close()
        handler.close()

    conteudo = log_path.read_text()
    assert "Tentativa 1/2" in conteudo
    assert "Tentativa 2/2" in conteudo
