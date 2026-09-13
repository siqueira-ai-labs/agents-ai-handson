"""Testes unitários — Ex02: Golden Dataset"""
import pathlib
import sys
from collections import Counter
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))

import ex02_golden_dataset_solucao as ex02


def test_modulo_importavel():
    assert ex02 is not None


def test_golden_dataset_tem_20_exemplos_com_cobertura_correta():
    dataset = ex02.build_golden_dataset()
    assert len(dataset.examples) == 20

    dificuldades = Counter(e.difficulty for e in dataset.examples)
    assert dificuldades == {"easy": 5, "medium": 10, "hard": 5}

    adversariais = sum(1 for e in dataset.examples if e.category == "adversarial")
    assert adversariais >= 3


def test_ids_sao_unicos():
    dataset = ex02.build_golden_dataset()
    ids = [e.id for e in dataset.examples]
    assert len(ids) == len(set(ids))


def test_save_e_load_roundtrip(tmp_path):
    dataset = ex02.build_golden_dataset()
    caminho = tmp_path / "golden.json"
    ex02.save_golden_dataset(dataset, path=caminho)

    carregado = ex02.load_golden_dataset(path=caminho)
    assert len(carregado.examples) == len(dataset.examples)
    assert carregado.examples[0].id == dataset.examples[0].id


def test_run_baseline_usa_a_chain_e_o_retriever():
    fake_chain = MagicMock()
    fake_chain.invoke.return_value = "resposta"
    fake_doc = SimpleNamespace(page_content="ctx")
    fake_retriever = MagicMock()
    fake_retriever.invoke.return_value = [fake_doc]

    dataset = ex02.GoldenDataset(examples=[
        ex02.GoldenExample(id="x1", question="pergunta?", ground_truth="resp", category="factual", difficulty="easy"),
    ])

    with patch.object(ex02, "build_llm", return_value=MagicMock()), \
         patch.object(ex02, "build_rag_chain", return_value=(fake_chain, fake_retriever)):
        resultados = ex02.run_baseline(dataset)

    assert len(resultados) == 1
    assert resultados[0]["answer"] == "resposta"
    assert resultados[0]["retrieved_contexts"] == ["ctx"]


def test_save_results(tmp_path):
    caminho = tmp_path / "results.json"
    ex02.save_results([{"id": "x1", "answer": "ok"}], path=caminho)
    assert caminho.exists()
    assert "x1" in caminho.read_text(encoding="utf-8")
