"""Testes unitários — Ex01: Bloqueio de PII"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex01_bloqueio_pii_solucao as ex01


@pytest.fixture(autouse=True)
def resetar_contadores():
    for k in ex01.pii_detection_count:
        ex01.pii_detection_count[k] = 0


def test_detecta_cpf():
    assert "cpf" in ex01.detect_pii("Meu CPF é 123.456.789-00")


def test_detecta_cartao_credito():
    assert "credit_card" in ex01.detect_pii("Cartão 4111 1111 1111 1111")


def test_detecta_email():
    assert "email" in ex01.detect_pii("Contato: usuario@exemplo.com")


def test_sem_pii():
    assert ex01.detect_pii("Qual é a cotação do Bitcoin?") == []


def test_sanitize_input_bloqueia_mensagem_com_pii():
    texto, tipos = ex01.sanitize_input("Meu e-mail é a@b.com")
    assert texto == ex01.BLOCKED_MESSAGE
    assert tipos == ["email"]


def test_sanitize_input_libera_mensagem_sem_pii():
    texto, tipos = ex01.sanitize_input("Qual o horário de atendimento?")
    assert texto == "Qual o horário de atendimento?"
    assert tipos == []


def test_contador_incrementa_por_tipo():
    ex01.detect_pii("CPF 111.222.333-44 e email a@b.com")
    assert ex01.pii_detection_count["cpf"] == 1
    assert ex01.pii_detection_count["email"] == 1
    assert ex01.pii_detection_count["credit_card"] == 0
