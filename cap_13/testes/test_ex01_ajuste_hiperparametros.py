"""Testes unitários — Ex01: Ajuste de Hiperparâmetros no LoRA"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex01_ajuste_hiperparametros_solucao as ex01


@pytest.fixture(scope="module")
def resultados():
    return ex01.run_all_experiments()


def test_modulo_importavel():
    assert ex01 is not None


def test_run_all_experiments_roda_as_tres_configs(resultados):
    assert len(resultados) == 3
    assert {r["label"] for r in resultados} == {"default", "larger", "lighter"}


def test_parametros_treinaveis_escalam_com_r(resultados):
    por_label = {r["label"]: r for r in resultados}
    # r=16 (larger) deve ter mais parâmetros treináveis que r=8 (default),
    # que por sua vez deve ter mais que r=4 (lighter).
    assert por_label["larger"]["trainable_params"] > por_label["default"]["trainable_params"]
    assert por_label["default"]["trainable_params"] > por_label["lighter"]["trainable_params"]


def test_cada_resultado_tem_loss_e_tempo(resultados):
    for r in resultados:
        assert r["loss"] > 0
        assert r["time_sec"] >= 0


def test_save_results_escreve_csv(tmp_path, resultados):
    caminho = tmp_path / "lora.csv"
    ex01.save_results(resultados, path=caminho)
    conteudo = caminho.read_text(encoding="utf-8")
    assert "label" in conteudo
    assert "default" in conteudo


def test_best_tradeoff_retorna_um_dos_resultados(resultados):
    melhor = ex01.best_tradeoff(resultados)
    assert melhor in resultados
