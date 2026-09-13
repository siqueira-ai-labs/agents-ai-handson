"""Testes unitários — Ex03: Quantização Extrema e Deploy Local"""
import pathlib
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex03_quantizacao_deploy_local_solucao as ex03


def test_modulo_importavel():
    assert ex03 is not None


def test_qlora_config_usa_nf4_4bit():
    assert ex03.QLORA_CONFIG.load_in_4bit is True
    assert ex03.QLORA_CONFIG.bnb_4bit_quant_type == "nf4"
    assert ex03.QLORA_CONFIG.bnb_4bit_use_double_quant is True


def test_lora_config_usa_target_modules_de_llama():
    assert ex03.LORA_CONFIG.r == 8
    assert set(ex03.LORA_CONFIG.target_modules) == {"q_proj", "v_proj"}


def test_convert_to_gguf_falha_com_mensagem_clara_sem_llama_cpp(tmp_path):
    with pytest.raises(FileNotFoundError, match="llama.cpp"):
        ex03.convert_to_gguf(merged_dir=tmp_path, gguf_path=tmp_path / "out.gguf")


def test_benchmark_inference_mede_latencia_por_query():
    fake_tokenizer = MagicMock()
    fake_tokenizer.return_value.to.return_value = {"input_ids": MagicMock()}
    fake_tokenizer.decode.return_value = "resposta gerada"

    fake_model = MagicMock()
    fake_model.device = "cpu"
    fake_model.generate.return_value = [MagicMock()]

    resultados = ex03.benchmark_inference(fake_model, fake_tokenizer, queries=["pergunta 1", "pergunta 2"])

    assert len(resultados) == 2
    for r in resultados:
        assert r["latency_sec"] >= 0
        assert r["output"] == "resposta gerada"
