"""Testes unitários — Ex01: Inspecionando o Estado no Postgres"""
import pathlib
import sys
from unittest.mock import MagicMock

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex01_inspecionar_estado_solucao as ex01


def _mock_conn(fetchall_return=None, description=None):
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchall.return_value = fetchall_return or []
    cursor.description = description or []
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn, cursor


def test_modulo_importavel():
    assert ex01 is not None


def test_list_threads_retorna_ids_unicos():
    conn, cursor = _mock_conn(fetchall_return=[("t1",), ("t2",)])
    resultado = ex01.list_threads(conn)
    assert resultado == ["t1", "t2"]
    cursor.execute.assert_called_once()
    assert "DISTINCT thread_id" in cursor.execute.call_args[0][0]


def test_get_thread_history_monta_dicts_por_coluna():
    description = [("thread_id",), ("checkpoint_id",), ("checkpoint_ns",), ("size_bytes",), ("metadata",)]
    rows = [("t1", "c1", "", 100, {}), ("t1", "c2", "", 150, {})]
    conn, cursor = _mock_conn(fetchall_return=rows, description=description)
    historico = ex01.get_thread_history(conn, "t1")
    assert len(historico) == 2
    assert historico[0]["checkpoint_id"] == "c1"
    assert historico[1]["size_bytes"] == 150
    args, _ = cursor.execute.call_args
    assert args[1] == ("t1",)


def test_summarize_thread_identifica_mais_antigo_e_mais_recente():
    historico = [{"checkpoint_id": "c1"}, {"checkpoint_id": "c2"}, {"checkpoint_id": "c3"}]
    resumo = ex01.summarize_thread(historico)
    assert resumo["oldest"]["checkpoint_id"] == "c1"
    assert resumo["newest"]["checkpoint_id"] == "c3"
    assert resumo["count"] == 3


def test_summarize_thread_vazio():
    resumo = ex01.summarize_thread([])
    assert resumo == {"oldest": None, "newest": None, "count": 0}
