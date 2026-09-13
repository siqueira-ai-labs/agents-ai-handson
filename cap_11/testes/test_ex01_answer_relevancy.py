"""Testes unitários — Ex01: Answer Relevancy no pipeline RAGAS"""
import pathlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))

import ex01_answer_relevancy_solucao as ex01


def test_modulo_importavel():
    assert ex01 is not None


def test_build_eval_dataset_usa_a_chain_e_o_retriever():
    fake_chain = MagicMock()
    fake_chain.invoke.return_value = "resposta simulada"
    fake_doc = SimpleNamespace(page_content="contexto simulado")
    fake_retriever = MagicMock()
    fake_retriever.invoke.return_value = [fake_doc]

    with patch.object(ex01, "build_llm", return_value=MagicMock()), \
         patch.object(ex01, "build_rag_chain", return_value=(fake_chain, fake_retriever)):
        dataset, llm = ex01.build_eval_dataset()

    assert len(dataset) == len(ex01.QUESTIONS)
    assert dataset["response"][0] == "resposta simulada"
    assert dataset["retrieved_contexts"][0] == ["contexto simulado"]
    assert "user_input" in dataset.column_names
    assert "reference" in dataset.column_names


def test_piores_answer_relevancy_retorna_as_n_menores():
    df = pd.DataFrame({
        "user_input": ["p1", "p2", "p3", "p4"],
        "answer_relevancy": [0.9, 0.2, 0.5, 0.1],
    })
    fake_result = SimpleNamespace(to_pandas=lambda: df)

    piores = ex01.piores_answer_relevancy(fake_result, n=2)

    perguntas = [p for p, _ in piores]
    assert perguntas == ["p4", "p2"]
