"""Testes unitários — Ex02: Webhook Receiver Seguro"""
import hashlib
import hmac
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex02_webhook_seguro_solucao as ex02

SECRET = b"minha-chave-secreta"


@pytest.fixture(autouse=True)
def configurar_secret_e_rate_limit():
    ex02.WEBHOOK_SECRET = SECRET
    ex02.request_log.clear()
    yield
    ex02.request_log.clear()


@pytest.fixture
def client():
    ex02.app.config["TESTING"] = True
    return ex02.app.test_client()


def assinar(body: bytes) -> str:
    return "sha256=" + hmac.new(SECRET, body, hashlib.sha256).hexdigest()


def test_verify_signature_valida():
    body = b'{"a": 1}'
    assert ex02.verify_signature(body, assinar(body)) is True


def test_verify_signature_invalida():
    body = b'{"a": 1}'
    assert ex02.verify_signature(body, "sha256=errado") is False


def test_verify_signature_vazia():
    assert ex02.verify_signature(b"{}", "") is False


def test_webhook_sem_assinatura_retorna_401(client):
    resp = client.post("/webhook/langflow", json={"outputs": []})
    assert resp.status_code == 401


def test_webhook_com_assinatura_valida_retorna_200(client):
    body = b'{"flow_id": "abc", "outputs": [{"outputs": [{"results": {"message": {"text": "ola"}}}]}]}'
    resp = client.post(
        "/webhook/langflow",
        data=body,
        headers={"Content-Type": "application/json", "X-Langflow-Signature": assinar(body)},
    )
    assert resp.status_code == 200
    assert resp.get_json()["processed"]["mensagens"] == ["ola"]


def test_check_rate_limit_bloqueia_apos_limite():
    ip = "1.2.3.4"
    resultados = [ex02.check_rate_limit(ip) for _ in range(ex02.RATE_LIMIT + 2)]
    assert resultados[: ex02.RATE_LIMIT] == [True] * ex02.RATE_LIMIT
    assert resultados[ex02.RATE_LIMIT:] == [False, False]


def test_process_langflow_payload_extrai_mensagens():
    payload = {
        "flow_id": "xyz",
        "outputs": [{"outputs": [{"results": {"message": {"text": "resposta 1"}}}]}],
    }
    processado = ex02.process_langflow_payload(payload)
    assert processado["flow_id"] == "xyz"
    assert processado["mensagens"] == ["resposta 1"]
