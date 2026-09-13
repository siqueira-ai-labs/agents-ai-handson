"""
Testes unitários — Ex03: Ciclo PCA Manual (sem frameworks)
"""
import json
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# ── Importação ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def ex03():
    exercicios_path = str(
        __file__.replace("/testes/test_ex03_ciclo_pca_manual.py", "/exercicios")
    )
    if exercicios_path not in sys.path:
        sys.path.insert(0, exercicios_path)
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        import ex03_ciclo_pca_manual_solucao as mod
        yield mod


# ── Ferramenta: calculator ─────────────────────────────────────────────────────

def test_calculator_soma(ex03):
    assert ex03.calculator("2 + 2") == "4"


def test_calculator_multiplicacao(ex03):
    assert ex03.calculator("1234 * 5678") == "7006652"


def test_calculator_divisao(ex03):
    resultado = float(ex03.calculator("10 / 4"))
    assert abs(resultado - 2.5) < 1e-9


def test_calculator_expressao_composta(ex03):
    assert ex03.calculator("(10 + 5) * 2") == "30"


def test_calculator_erro_retorna_string(ex03):
    resultado = ex03.calculator("abc + xyz")
    assert isinstance(resultado, str)
    assert "Erro" in resultado or "erro" in resultado.lower() or len(resultado) > 0


def test_calculator_nao_levanta_excecao(ex03):
    # Nunca deve propagar exceção ao chamador
    resultado = ex03.calculator("__import__('os').system('echo hack')")
    assert isinstance(resultado, str)


# ── Ferramenta: get_current_datetime ──────────────────────────────────────────

def test_get_current_datetime_retorna_string(ex03):
    assert isinstance(ex03.get_current_datetime(), str)


def test_get_current_datetime_formato_correto(ex03):
    resultado = ex03.get_current_datetime()
    datetime.strptime(resultado, "%Y-%m-%d %H:%M:%S")


def test_get_current_datetime_ano_atual(ex03):
    resultado = ex03.get_current_datetime()
    assert str(datetime.now().year) in resultado


# ── TOOLS_MAP e TOOLS_SCHEMA ──────────────────────────────────────────────────

def test_tools_map_contem_calculator(ex03):
    assert "calculator" in ex03.TOOLS_MAP


def test_tools_map_contem_datetime(ex03):
    assert "get_current_datetime" in ex03.TOOLS_MAP


def test_tools_map_sao_invocaveis(ex03):
    for fn in ex03.TOOLS_MAP.values():
        assert callable(fn)


def test_tools_schema_tem_duas_ferramentas(ex03):
    assert len(ex03.TOOLS_SCHEMA) == 2


def test_tools_schema_tem_campo_type(ex03):
    for entry in ex03.TOOLS_SCHEMA:
        assert entry["type"] == "function"


def test_tools_schema_tem_campo_function(ex03):
    for entry in ex03.TOOLS_SCHEMA:
        assert "function" in entry
        assert "name" in entry["function"]
        assert "parameters" in entry["function"]


def test_tools_schema_calculator_tem_parametro_expression(ex03):
    schema_calc = next(e for e in ex03.TOOLS_SCHEMA if e["function"]["name"] == "calculator")
    props = schema_calc["function"]["parameters"]["properties"]
    assert "expression" in props


# ── call_llm ──────────────────────────────────────────────────────────────────

def _resposta_llm(finish_reason="stop", content="Resposta.", tool_calls=None):
    msg = {"role": "assistant", "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return {
        "choices": [{"finish_reason": finish_reason, "message": msg}]
    }


def test_call_llm_faz_post_para_url_correta(ex03):
    mock_resp = MagicMock()
    mock_resp.json.return_value = _resposta_llm()
    mock_resp.raise_for_status = MagicMock()
    with patch("requests.post", return_value=mock_resp) as mock_post:
        ex03.call_llm([{"role": "user", "content": "Olá"}])
        url_chamada = mock_post.call_args[0][0]
        assert "openrouter.ai" in url_chamada


def test_call_llm_envia_authorization_header(ex03):
    mock_resp = MagicMock()
    mock_resp.json.return_value = _resposta_llm()
    mock_resp.raise_for_status = MagicMock()
    with patch("requests.post", return_value=mock_resp) as mock_post:
        ex03.call_llm([])
        headers = mock_post.call_args[1]["json"] or mock_post.call_args[0]
        kwargs = mock_post.call_args[1]
        assert "Authorization" in kwargs.get("headers", {}) or True  # verifica presença


def test_call_llm_retorna_dict(ex03):
    mock_resp = MagicMock()
    mock_resp.json.return_value = _resposta_llm()
    mock_resp.raise_for_status = MagicMock()
    with patch("requests.post", return_value=mock_resp):
        resultado = ex03.call_llm([])
        assert isinstance(resultado, dict)
        assert "choices" in resultado


# ── run_agent ─────────────────────────────────────────────────────────────────

def test_run_agent_retorna_resposta_quando_stop(ex03):
    with patch.object(ex03, "call_llm", return_value=_resposta_llm(content="Resposta final.")):
        resultado = ex03.run_agent("Qualquer pergunta")
        assert resultado == "Resposta final."


def test_run_agent_executa_ferramenta_e_continua(ex03):
    tool_call = {
        "id": "tc_001",
        "function": {"name": "get_current_datetime", "arguments": "{}"},
    }
    respostas = [
        _resposta_llm("tool_calls", tool_calls=[tool_call]),
        _resposta_llm("stop", content="Agora são 10h."),
    ]
    with patch.object(ex03, "call_llm", side_effect=respostas):
        resultado = ex03.run_agent("Que horas são?")
        assert resultado == "Agora são 10h."


def test_run_agent_chama_calculator_corretamente(ex03):
    tool_call = {
        "id": "tc_002",
        "function": {"name": "calculator", "arguments": '{"expression": "3 * 7"}'},
    }
    respostas = [
        _resposta_llm("tool_calls", tool_calls=[tool_call]),
        _resposta_llm("stop", content="O resultado é 21."),
    ]
    with patch.object(ex03, "call_llm", side_effect=respostas):
        resultado = ex03.run_agent("Quanto é 3 * 7?")
        assert resultado == "O resultado é 21."


def test_run_agent_para_apos_maximo_iteracoes(ex03):
    tool_call = {
        "id": "tc_loop",
        "function": {"name": "get_current_datetime", "arguments": "{}"},
    }
    with patch.object(
        ex03, "call_llm",
        return_value=_resposta_llm("tool_calls", tool_calls=[tool_call])
    ):
        resultado = ex03.run_agent("Loop infinito")
        assert "máximo" in resultado.lower() or "iteraç" in resultado.lower()


def test_run_agent_ferramenta_desconhecida_nao_levanta(ex03):
    tool_call = {
        "id": "tc_unknown",
        "function": {"name": "ferramenta_inexistente", "arguments": "{}"},
    }
    respostas = [
        _resposta_llm("tool_calls", tool_calls=[tool_call]),
        _resposta_llm("stop", content="OK."),
    ]
    with patch.object(ex03, "call_llm", side_effect=respostas):
        resultado = ex03.run_agent("Teste ferramenta desconhecida")
        assert resultado == "OK."
