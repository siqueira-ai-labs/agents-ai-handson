"""Testes unitários — Ex03: Controle de Concorrência Otimista"""
import pathlib
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex03_controle_concorrencia_solucao as ex03


def _mock_conn(fetchone_side_effect=None):
    conn = MagicMock()
    cursor = MagicMock()
    if fetchone_side_effect is not None:
        cursor.fetchone.side_effect = fetchone_side_effect
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn, cursor


def test_modulo_importavel():
    assert ex03 is not None


def test_optimistic_update_bem_sucedido():
    conn, cursor = _mock_conn(fetchone_side_effect=[(5,)])
    nova_versao = ex03.optimistic_update(conn, "t1", expected_version=4, new_state={"x": 1})
    assert nova_versao == 5
    conn.commit.assert_called_once()


def test_optimistic_update_levanta_conflito_quando_versao_diverge():
    conn, cursor = _mock_conn(fetchone_side_effect=[None])
    with pytest.raises(ex03.ConcurrencyConflictError):
        ex03.optimistic_update(conn, "t1", expected_version=4, new_state={"x": 1})


def test_update_with_retry_sucesso_na_primeira_tentativa():
    conn, cursor = _mock_conn(fetchone_side_effect=[(3,), (4,)])
    resultado = ex03.update_with_retry(conn, "t1", {"x": 1}, max_retries=3)
    assert resultado == 4


def test_update_with_retry_recupera_apos_conflito(monkeypatch):
    # 1ª iteração: SELECT version -> 3; UPDATE falha (conflito, fetchone None)
    # 2ª iteração: SELECT version -> 4 (mudou); UPDATE sucesso -> 5
    conn, cursor = _mock_conn(fetchone_side_effect=[(3,), None, (4,), (5,)])
    monkeypatch.setattr(ex03.time, "sleep", lambda s: None)  # não esperar de verdade no teste
    resultado = ex03.update_with_retry(conn, "t1", {"x": 1}, max_retries=3)
    assert resultado == 5


def test_update_with_retry_esgota_tentativas_e_propaga_conflito(monkeypatch):
    # Toda tentativa: SELECT retorna versão, UPDATE sempre conflita (None)
    side_effects = []
    for _ in range(3):
        side_effects += [(1,), None]
    conn, cursor = _mock_conn(fetchone_side_effect=side_effects)
    monkeypatch.setattr(ex03.time, "sleep", lambda s: None)
    with pytest.raises(ex03.ConcurrencyConflictError):
        ex03.update_with_retry(conn, "t1", {"x": 1}, max_retries=3)


def test_update_with_retry_thread_inexistente_levanta_value_error():
    conn, cursor = _mock_conn(fetchone_side_effect=[None])
    with pytest.raises(ValueError):
        ex03.update_with_retry(conn, "thread-fantasma", {"x": 1})
