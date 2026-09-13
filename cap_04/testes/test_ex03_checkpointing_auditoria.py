"""Testes unitários — Ex03: Checkpointing e Auditoria"""
import os
import sys
import pathlib
import tempfile
import sqlite3
from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage, HumanMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))


@pytest.fixture(scope="module")
def ex03():
    mock_llm = MagicMock()
    mock_llm.return_value = AIMessage(content="ok", tool_calls=[])
    mock_llm.bind_tools.return_value = mock_llm

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex03_checkpointing_auditoria_solucao as mod
            yield mod


@pytest.fixture()
def tmp_db(tmp_path):
    return str(tmp_path / "test_checkpoints.db")


def test_modulo_importavel(ex03):
    assert ex03 is not None


def test_list_sessions_existe(ex03):
    assert callable(ex03.list_sessions)


def test_get_session_history_existe(ex03):
    assert callable(ex03.get_session_history)


def test_print_audit_report_existe(ex03):
    assert callable(ex03.print_audit_report)


def test_list_sessions_db_vazio(ex03, tmp_db):
    sessions = ex03.list_sessions(tmp_db)
    assert sessions == []


def test_list_sessions_apos_insert(ex03, tmp_db):
    conn = sqlite3.connect(tmp_db)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS checkpoints "
        "(thread_id TEXT, checkpoint_ns TEXT, checkpoint_id TEXT, parent_checkpoint_id TEXT, "
        "type TEXT, checkpoint BLOB, metadata BLOB)"
    )
    conn.execute("INSERT INTO checkpoints (thread_id) VALUES ('sessao-1')")
    conn.execute("INSERT INTO checkpoints (thread_id) VALUES ('sessao-2')")
    conn.commit()
    conn.close()

    sessions = ex03.list_sessions(tmp_db)
    assert "sessao-1" in sessions
    assert "sessao-2" in sessions


def test_build_app_retorna_compilado(ex03, tmp_db):
    app, checkpointer = ex03.build_app(tmp_db)
    assert app is not None
    assert checkpointer is not None


def test_print_audit_report_sem_sessoes(ex03, tmp_db, capsys):
    ex03.print_audit_report(tmp_db)
    captured = capsys.readouterr()
    assert "nenhuma" in captured.out.lower() or captured.out.strip() == ""


def test_db_path_definido(ex03):
    assert hasattr(ex03, "DB_PATH")
    assert ex03.DB_PATH.endswith(".db")
