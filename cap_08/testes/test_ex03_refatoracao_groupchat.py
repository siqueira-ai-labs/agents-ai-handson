"""Testes unitários — Ex03: Pipeline de Refatoração com GroupChat"""
import os
import pathlib
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from autogen_agentchat.teams import SelectorGroupChat

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))


@pytest.fixture(scope="module")
def ex03():
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        import ex03_refatoracao_groupchat_solucao as mod
        yield mod


def test_modulo_importavel(ex03):
    assert ex03 is not None


def test_build_team_participantes_e_termino(ex03):
    client = ex03.build_model_client()
    team = ex03.build_team(client)
    assert isinstance(team, SelectorGroupChat)
    nomes = [p.name for p in team._participants]
    assert nomes == ["Analyzer", "Refactorer", "Tester", "Reviewer"]


def test_extract_last_code_block_encontra_bloco_do_refactorer(ex03):
    mensagens = [
        SimpleNamespace(source="user", content="tarefa"),
        SimpleNamespace(source="Analyzer", content="Nomes ruins, sem tipagem."),
        SimpleNamespace(
            source="Refactorer",
            content="Aqui está:\n```python\ndef calc(x: int, y: int, z: int) -> int:\n    return x * y * z\n```",
        ),
        SimpleNamespace(source="Reviewer", content="APPROVED"),
    ]
    codigo = ex03.extract_last_code_block(mensagens, source="Refactorer")
    assert "def calc(x: int, y: int, z: int) -> int:" in codigo


def test_extract_last_code_block_sem_bloco_retorna_none(ex03):
    mensagens = [SimpleNamespace(source="Refactorer", content="Sem código ainda.")]
    assert ex03.extract_last_code_block(mensagens, source="Refactorer") is None


@pytest.mark.asyncio
async def test_run_salva_codigo_refatorado(ex03, tmp_path, monkeypatch):
    monkeypatch.setattr(ex03, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(ex03, "OUTPUT_PATH", tmp_path / "refactored.py")

    fake_result = SimpleNamespace(
        messages=[
            SimpleNamespace(source="Refactorer", content="```python\ndef calc(x, y, z):\n    return x * y * z\n```"),
            SimpleNamespace(source="Reviewer", content="APPROVED"),
        ]
    )
    fake_team = SimpleNamespace(run=AsyncMock(return_value=fake_result))
    fake_client = SimpleNamespace(close=AsyncMock())

    with patch.object(ex03, "build_model_client", return_value=fake_client), \
         patch.object(ex03, "build_team", return_value=fake_team):
        caminho = await ex03.run("refatore isso")

    assert caminho == str(tmp_path / "refactored.py")
    assert "def calc(x, y, z):" in (tmp_path / "refactored.py").read_text()
    fake_client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_sem_codigo_retorna_none(ex03, tmp_path, monkeypatch):
    monkeypatch.setattr(ex03, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(ex03, "OUTPUT_PATH", tmp_path / "refactored.py")

    fake_result = SimpleNamespace(
        messages=[SimpleNamespace(source="Analyzer", content="Ainda analisando.")]
    )
    fake_team = SimpleNamespace(run=AsyncMock(return_value=fake_result))
    fake_client = SimpleNamespace(close=AsyncMock())

    with patch.object(ex03, "build_model_client", return_value=fake_client), \
         patch.object(ex03, "build_team", return_value=fake_team):
        caminho = await ex03.run("refatore isso")

    assert caminho is None
    assert not (tmp_path / "refactored.py").exists()
