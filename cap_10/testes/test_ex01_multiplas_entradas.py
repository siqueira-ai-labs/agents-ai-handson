"""Testes unitários — Ex01: Múltiplas Entradas via Tweaks"""
import pathlib
import sys
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex01_multiplas_entradas_solucao as ex01


def test_build_tweaks_inclui_nome_idioma_tom():
    tweaks = ex01.build_tweaks("Ana", "português", "formal")
    valores = str(tweaks)
    assert "Ana" in valores
    assert "português" in valores
    assert "formal" in valores


def test_run_personalized_chama_run_flow_com_tweaks():
    with patch.object(ex01, "run_flow", return_value={"outputs": "ok"}) as mock_run:
        resultado = ex01.run_personalized("oi", "Ana", "português", "formal")
    assert resultado == {"outputs": "ok"}
    args, kwargs = mock_run.call_args
    assert args[0] == "oi"
    assert "tweaks" in kwargs
