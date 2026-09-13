"""Testes unitários — Ex03: Moderação de Saída com Llama Guard"""
import pathlib
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex03_moderacao_llama_guard_solucao as ex03


def test_modulo_importavel():
    assert ex03 is not None


def test_parse_response_safe():
    assert ex03._parse_llama_guard_response("safe") == (True, None)


def test_parse_response_unsafe_com_categoria():
    safe, categoria = ex03._parse_llama_guard_response("unsafe\nS9,S1")
    assert safe is False
    assert categoria == "s9,s1"


def test_parse_response_inesperada_falha_aberto():
    assert ex03._parse_llama_guard_response("???") == (True, None)


def test_moderate_output_aprova_quando_ollama_diz_safe():
    fake_response = MagicMock()
    fake_response.json.return_value = {"response": "safe"}
    fake_response.raise_for_status.return_value = None

    with patch("requests.post", return_value=fake_response):
        resposta, bloqueada = ex03.moderate_output("A Selic está em 10,5% ao ano.")

    assert bloqueada is False
    assert resposta == "A Selic está em 10,5% ao ano."


def test_moderate_output_bloqueia_quando_ollama_diz_unsafe():
    fake_response = MagicMock()
    fake_response.json.return_value = {"response": "unsafe\nS6"}
    fake_response.raise_for_status.return_value = None

    with patch("requests.post", return_value=fake_response):
        resposta, bloqueada = ex03.moderate_output("resposta arriscada")

    assert bloqueada is True
    assert resposta == ex03.SAFE_FALLBACK


def test_moderate_output_falha_aberto_quando_ollama_indisponivel():
    with patch("requests.post", side_effect=ConnectionError("sem conexão")):
        resposta, bloqueada = ex03.moderate_output("resposta qualquer")

    assert bloqueada is False
    assert resposta == "resposta qualquer"


def test_hash_content_nao_reversivel_e_deterministico():
    h1 = ex03.hash_content("dado sensível")
    h2 = ex03.hash_content("dado sensível")
    assert h1 == h2
    assert "dado sensível" not in h1


def test_create_moderation_middleware_registra_rota():
    from flask import Flask

    app = Flask(__name__)
    ex03.create_moderation_middleware(app, agent_fn=lambda msg: f"echo: {msg}")

    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"response": "safe"}
        mock_post.return_value.raise_for_status.return_value = None
        client = app.test_client()
        resp = client.post("/chat/moderated", json={"message": "oi"})

    assert resp.status_code == 200
    assert resp.get_json()["response"] == "echo: oi"
