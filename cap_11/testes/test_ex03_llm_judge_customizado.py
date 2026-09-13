"""Testes unitários — Ex03: LLM-as-a-Judge Customizado"""
import pathlib
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex03_llm_judge_customizado_solucao as ex03


def test_modulo_importavel():
    assert ex03 is not None


def test_pearson_correlation_perfeita():
    assert ex03.pearson_correlation([0.1, 0.5, 0.9], [0.1, 0.5, 0.9]) == pytest.approx(1.0)


def test_pearson_correlation_anticorrelacao():
    assert ex03.pearson_correlation([0.1, 0.5, 0.9], [0.9, 0.5, 0.1]) == pytest.approx(-1.0)


def test_pearson_correlation_sem_variancia_retorna_zero():
    assert ex03.pearson_correlation([0.5, 0.5, 0.5], [0.1, 0.9, 0.3]) == 0.0


def test_evaluate_response_invoca_a_chain():
    fake_score = ex03.JudgeScore(
        safety=0.9, completeness=0.8, citation_quality=0.7, tone_appropriateness=1.0,
        overall=0.85, reasoning="ok",
    )
    with patch.object(ex03, "judge_chain") as mock_chain:
        mock_chain.invoke.return_value = fake_score
        resultado = ex03.evaluate_response("pergunta", "resposta", "contexto")
    assert resultado == fake_score
    mock_chain.invoke.assert_called_once_with({"question": "pergunta", "answer": "resposta", "context": "contexto"})


def test_calibrate_against_humans_calcula_correlacao():
    scores = [
        ex03.JudgeScore(safety=1, completeness=1, citation_quality=1, tone_appropriateness=1, overall=0.2, reasoning="a"),
        ex03.JudgeScore(safety=1, completeness=1, citation_quality=1, tone_appropriateness=1, overall=0.5, reasoning="b"),
        ex03.JudgeScore(safety=1, completeness=1, citation_quality=1, tone_appropriateness=1, overall=0.9, reasoning="c"),
    ]
    calibration_set = [
        {"question": "q1", "answer": "a1", "context": "c1", "human_overall": 0.3},
        {"question": "q2", "answer": "a2", "context": "c2", "human_overall": 0.6},
        {"question": "q3", "answer": "a3", "context": "c3", "human_overall": 0.85},
    ]
    with patch.object(ex03, "evaluate_response", side_effect=scores):
        resultado = ex03.calibrate_against_humans(calibration_set)

    assert resultado["n"] == 3
    assert resultado["llm_scores"] == [0.2, 0.5, 0.9]
    assert resultado["pearson_correlation"] > 0.9


def test_generate_html_report_contem_pergunta_e_scores(tmp_path):
    fake_score = SimpleNamespace(
        safety=0.9, completeness=0.8, citation_quality=0.7, tone_appropriateness=1.0,
        overall=0.85, reasoning="justificativa de teste",
    )
    caminho = tmp_path / "report.html"
    resultado = ex03.generate_html_report(
        [{"question": "Minha pergunta?", "scores": fake_score}], output_path=str(caminho)
    )
    conteudo = pathlib.Path(resultado).read_text(encoding="utf-8")
    assert "Minha pergunta?" in conteudo
    assert "justificativa de teste" in conteudo
    assert "0.85" in conteudo
