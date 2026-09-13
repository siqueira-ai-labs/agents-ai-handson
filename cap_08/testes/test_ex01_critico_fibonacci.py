"""Testes unitários — Ex01: Crítico ao Fibonacci"""
import os
import pathlib
import sys
from unittest.mock import patch

import pytest
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.replay import ReplayChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

MODEL_INFO = ModelInfo(
    vision=False,
    function_calling=False,
    json_output=False,
    family=ModelFamily.UNKNOWN,
    structured_output=False,
)


@pytest.fixture(scope="module")
def ex01():
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        import ex01_critico_fibonacci_solucao as mod
        yield mod


def test_modulo_importavel(ex01):
    assert ex01 is not None


def test_build_model_client(ex01):
    client = ex01.build_model_client()
    assert client is not None


def test_build_team_tem_os_tres_agentes(ex01):
    client = ex01.build_model_client()
    team = ex01.build_team(client)
    assert isinstance(team, RoundRobinGroupChat)
    nomes = [p.name for p in team._participants]
    assert nomes == ["assistant", "critic", "code_executor"]


@pytest.mark.asyncio
async def test_fluxo_completo_executa_codigo_aprovado(ex01, tmp_path, monkeypatch):
    monkeypatch.setattr(ex01, "CODING_DIR", tmp_path)
    replies = [
        "```python\ndef fib(n, memo={}):\n"
        "    if n in memo:\n        return memo[n]\n"
        "    if n <= 1:\n        return n\n"
        "    memo[n] = fib(n - 1, memo) + fib(n - 2, memo)\n"
        "    return memo[n]\n"
        "print(fib(40))\n```",
        "Aprovado para execução.",
    ]
    client = ReplayChatCompletionClient(replies, model_info=MODEL_INFO)
    try:
        team = ex01.build_team(client)
        result = await team.run(task="Fibonacci com memoização, n=40")
    finally:
        await client.close()

    sources = [m.source for m in result.messages]
    assert sources == ["user", "assistant", "critic", "code_executor"]
    assert "102334155" in result.messages[-1].content
